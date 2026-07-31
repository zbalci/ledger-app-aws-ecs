#!/usr/bin/env bash

set -Eeuo pipefail

########################################
# Configuration
########################################

APP_NAME="ledger"
ENVIRONMENT="dev"
AWS_REGION="eu-north-1"

GITHUB_CONNECTION_ARN="arn:aws:codeconnections:eu-north-1:253712034003:connection/2c02ecd9-b115-4cec-967f-a0e4445ecfaa"

SOURCE_REPO="zbalci/ledger-app-aws-ecs"

########################################
# Colors
########################################

GREEN="\033[0;32m"
BLUE="\033[0;34m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
NC="\033[0m"

########################################
# Helper functions
########################################

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[ OK ]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

trap 'error "Deployment failed on line $LINENO."' ERR

########################################
# Sync templates function
########################################

sync_templates() {

    local IAC_S3_URL

    IAC_S3_URL=$(get_ssm_parameter "/${APP_NAME}/${ENVIRONMENT}/iac_bucket_s3")

    info "Uploading CloudFormation templates..."

    aws s3 sync \
        infrastructure/cloudformation \
        "$IAC_S3_URL"

    success "Templates uploaded."
}

########################################
# Get SSM Parameter Function
########################################

get_ssm_parameter() {

    aws ssm get-parameter \
        --name "$1" \
        --query "Parameter.Value" \
        --output text \
        --region "$AWS_REGION"
}

########################################
# Deploy stack function
########################################

deploy_stack() {

    local STACK_NAME="$1"
    local TEMPLATE="$2"

    shift 2

    #
    # Eğer kullanıcı "global", "foundation" veya "app"
    # gibi bir klasör adı verdiyse TemplateURL oluştur.
    #
    if [[ "$TEMPLATE" != *.yaml ]]; then
        TEMPLATE="$(get_ssm_parameter "/${APP_NAME}/iac_bucket_url")/stack.yaml"
    fi

    local TEMPLATE_OPTION

    if [[ "$TEMPLATE" =~ ^https?:// ]]; then
        TEMPLATE_OPTION="--template-url"
    else
        TEMPLATE_OPTION="--template-body"
        TEMPLATE="file://${TEMPLATE}"
    fi

    info "Deploying stack: ${STACK_NAME}"

    if aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$AWS_REGION" \
        >/dev/null 2>&1
    then

        info "Updating existing stack..."

        if ! UPDATE_OUTPUT=$(
            aws cloudformation update-stack \
                --stack-name "$STACK_NAME" \
                "$TEMPLATE_OPTION" "$TEMPLATE" \
                --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
                "$@" \
                --region "$AWS_REGION" \
                2>&1
        ); then

            if [[ "$UPDATE_OUTPUT" == *"No updates are to be performed."* ]]; then
                info "No changes detected."
            else
                error "Update failed."
                echo "$UPDATE_OUTPUT"
                exit 1
            fi

        else

            aws cloudformation wait stack-update-complete \
                --stack-name "$STACK_NAME" \
                --region "$AWS_REGION"

            success "Stack updated."

        fi

    else

        info "Creating new stack..."

        aws cloudformation create-stack \
            --stack-name "$STACK_NAME" \
            "$TEMPLATE_OPTION" "$TEMPLATE" \
            --disable-rollback \
            --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
            "$@" \
            --region "$AWS_REGION"

        aws cloudformation wait stack-create-complete \
            --stack-name "$STACK_NAME" \
            --region "$AWS_REGION"

        success "Stack created."

    fi
}

usage() {

cat << EOF

Usage:

    ./deploy.sh [option]

Options
    --help             Show this help (default)

    --all              Deploy everything 

    --foundation-only  Deploy foundation stack

    --root-only  Deploy foundation stack

Examples:
    ./deploy.sh --all
    ./deploy.sh --foundation-only
EOF

}

SHOW_HELP=true

DEPLOY_FOUNDATION=false
DEPLOY_ROOT=false

while [[ $# -gt 0 ]]; do
    case "$1" in

        --all)
            SHOW_HELP=false
            DEPLOY_FOUNDATION=true
            DEPLOY_ROOT=true
            ;;

        --foundation-only)
            SHOW_HELP=false
            DEPLOY_ROOT=false
            DEPLOY_FOUNDATION=true
            ;;

        --root-only)
            SHOW_HELP=false
            DEPLOY_ROOT=true
            DEPLOY_FOUNDATION=false
            ;;

        --help|-h)
            usage
            exit 0
            ;;

        *)
            echo "Unknown option: $1"
            echo
            usage
            exit 1
            ;;

    esac

    shift
done

if $SHOW_HELP; then
    usage
    exit 0
fi

main() {
    #
    # Global/Foundation/App için template'leri yükle
    #

    if $DEPLOY_FOUNDATION; then
        deploy_stack \
            "${APP_NAME}-${ENVIRONMENT}-foundation"  \
            infrastructure/cloudformation/foundation/root.yaml \
            --parameters \
                ParameterKey=AppName,ParameterValue="$APP_NAME" \
                ParameterKey=Environment,ParameterValue="$ENVIRONMENT"

    fi

    if $DEPLOY_ROOT; then
        sync_templates
        
        IAC_HTTP_URL=$(get_ssm_parameter "/${APP_NAME}/${ENVIRONMENT}/iac_bucket_url")

        deploy_stack \
            "${APP_NAME}-${ENVIRONMENT}-root" \
            "${IAC_HTTP_URL}/root.yaml" \
            --parameters \
                ParameterKey=AppName,ParameterValue="$APP_NAME" \
                ParameterKey=Environment,ParameterValue="$ENVIRONMENT" \
                ParameterKey=GithubConnectionArn,ParameterValue="$GITHUB_CONNECTION_ARN" \
                ParameterKey=SourceRepo,ParameterValue="$SOURCE_REPO" 
        fi

}

main "$@"