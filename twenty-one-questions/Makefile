.PHONY: lint build deploy destroy clean test build-amplify

LAMBDA_DIR := tq-lambda
INFRA_DIR := infra
BUILD_DIR := build
PACKAGE_NAME := lambda-deployment.zip
VENV_DIR := venv
VENV := $(VENV_DIR)/bin
WEB_DIR := tq-web
AMPLIFY_BUILD_DIR := amplify-build
AMPLIFY_PACKAGE := amplify-deployment.zip

lint:
	@python3 -m pip install black flake8 autopep8 autoflake --quiet 2>/dev/null || true
	@python3 -m autoflake --in-place --remove-all-unused-imports --recursive --exclude=__pycache__ $(LAMBDA_DIR) $(INFRA_DIR)
	@python3 -m black --line-length=100 $(LAMBDA_DIR) $(INFRA_DIR)
	@python3 -m autopep8 --in-place --aggressive --aggressive --max-line-length=100 --recursive --exclude=__pycache__ $(LAMBDA_DIR) $(INFRA_DIR)
	@python3 -m flake8 $(LAMBDA_DIR) $(INFRA_DIR) --max-line-length=100 --exclude=__pycache__,*.pyc || true

build: clean
	@mkdir -p $(BUILD_DIR)
	@python3 install_linux_deps.py $(LAMBDA_DIR)/requirements.txt $(BUILD_DIR)
	@cp -r $(LAMBDA_DIR)/*.py $(BUILD_DIR)/ 2>/dev/null || true
	@cp -r $(LAMBDA_DIR)/langchain $(BUILD_DIR)/ 2>/dev/null || true
	@cp -r $(LAMBDA_DIR)/lib $(BUILD_DIR)/ 2>/dev/null || true
	@cp -r $(LAMBDA_DIR)/database $(BUILD_DIR)/ 2>/dev/null || true
	@cp -r ../common-lib/llm $(BUILD_DIR)/ 2>/dev/null || true
	@cd $(BUILD_DIR) && zip -r ../$(PACKAGE_NAME) . -x "*.pyc" -x "__pycache__/*" -x "*.dist-info/*" -x "*.egg-info/*" > /dev/null

deploy: build
	@cd $(INFRA_DIR) && pip3 install -r requirements.txt --quiet
	@cd $(INFRA_DIR) && npx -y cdktf-cli@latest get
	@cd $(INFRA_DIR) && npx -y cdktf-cli@latest deploy --auto-approve
	@cd $(INFRA_DIR) && npx -y cdktf-cli@latest output function_url_output --json 2>/dev/null | python3 -c "import sys, json; url=json.load(sys.stdin).get('value',''); print(f'\nFunction URL: {url}\n' if url else ''); print(f'curl -X POST {url} -H \"Content-Type: application/json\" -d \'{{\"sessionKey\": \"your-session-key\"}}\'' if url else 'aws lambda get-function-url-config --function-name tq-lambda --query FunctionUrl --output text')" 2>/dev/null || echo "aws lambda get-function-url-config --function-name tq-lambda --query FunctionUrl --output text"

destroy:
	@cd $(INFRA_DIR) && npx -y cdktf-cli@latest destroy --auto-approve

test: $(VENV_DIR)
	@$(VENV)/pip install -r $(LAMBDA_DIR)/requirements.txt --quiet
	@$(VENV)/pip install pytest --quiet
	@$(VENV)/pytest $(LAMBDA_DIR) $(INFRA_DIR) -v || true

$(VENV_DIR):
	@python3 -m venv $(VENV_DIR)
	@$(VENV)/pip install --upgrade pip --quiet

build-amplify: clean-amplify
	@echo "Preparing web app for AWS Amplify deployment..."
	@cd $(WEB_DIR) && npm ci
	@echo "Building SvelteKit app..."
	@cd $(WEB_DIR) && npm run build
	@echo "Creating Amplify deployment package..."
	@mkdir -p $(AMPLIFY_BUILD_DIR)
	@cd $(WEB_DIR) && zip -r ../$(AMPLIFY_PACKAGE) . \
		-x "node_modules/*" \
		-x ".svelte-kit/*" \
		-x "build/*" \
		-x "*.log" \
		-x ".DS_Store" \
		-x "__pycache__/*" \
		-x "*.pyc" \
		-x ".git/*" \
		-x ".vscode/*" \
		-x ".idea/*" \
		-x "*.swp" \
		-x "*.swo" \
		> /dev/null
	@echo ""
	@echo "✓ Amplify deployment package created: $(AMPLIFY_PACKAGE)"
	@echo "✓ Package size: $$(du -h $(AMPLIFY_PACKAGE) | cut -f1)"
	@echo ""
	@echo "To deploy to AWS Amplify:"
	@echo "  1. Upload $(AMPLIFY_PACKAGE) to your Amplify app"
	@echo "  2. Or connect your Git repository to Amplify (recommended)"
	@echo "  3. Amplify will use amplify.yml for build configuration"

clean-amplify:
	@rm -rf $(AMPLIFY_BUILD_DIR) $(AMPLIFY_PACKAGE)
	@cd $(WEB_DIR) && rm -rf .svelte-kit build node_modules/.vite 2>/dev/null || true

clean: clean-amplify
	@rm -rf $(BUILD_DIR) $(PACKAGE_NAME) $(VENV_DIR) $(INFRA_DIR)/cdktf.out $(INFRA_DIR)/imports
	@find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
