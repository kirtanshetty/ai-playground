.PHONY: lint build deploy destroy clean test

LAMBDA_DIR := tq-lambda
INFRA_DIR := infra
BUILD_DIR := build
PACKAGE_NAME := lambda-deployment.zip
VENV_DIR := venv
VENV := $(VENV_DIR)/bin

lint:
	@python3 -m pip install black flake8 autopep8 autoflake --quiet 2>/dev/null || true
	@python3 -m autoflake --in-place --remove-all-unused-imports --recursive --exclude=__pycache__ $(LAMBDA_DIR) $(INFRA_DIR)
	@python3 -m black --line-length=100 $(LAMBDA_DIR) $(INFRA_DIR)
	@python3 -m autopep8 --in-place --aggressive --aggressive --max-line-length=100 --recursive --exclude=__pycache__ $(LAMBDA_DIR) $(INFRA_DIR)
	@python3 -m flake8 $(LAMBDA_DIR) $(INFRA_DIR) --max-line-length=100 --exclude=__pycache__,*.pyc || true

build: clean
	@mkdir -p $(BUILD_DIR)
	@pip3 install -r $(LAMBDA_DIR)/requirements.txt -t $(BUILD_DIR) --quiet
	@cp -r $(LAMBDA_DIR)/*.py $(BUILD_DIR)/ 2>/dev/null || true
	@cp -r $(LAMBDA_DIR)/langchain $(BUILD_DIR)/ 2>/dev/null || true
	@cd $(BUILD_DIR) && zip -r ../$(PACKAGE_NAME) . -x "*.pyc" -x "__pycache__/*" -x "*.dist-info/*" -x "*.egg-info/*" > /dev/null

deploy: build
	@cd $(INFRA_DIR) && pip3 install -r requirements.txt --quiet
	@cd $(INFRA_DIR) && (cdk bootstrap 2>/dev/null || npx -y aws-cdk bootstrap) || true
	@cd $(INFRA_DIR) && (cdk deploy --require-approval never --outputs-file ../cdk-outputs.json 2>/dev/null || npx -y aws-cdk deploy --require-approval never --outputs-file ../cdk-outputs.json)
	@python3 -c "import json; d=json.load(open('cdk-outputs.json')); url=d.get('TQLambdaStack',{}).get('FunctionUrl',''); print(f'\nFunction URL: {url}\n' if url else ''); print(f'curl -X POST {url} -H \"Content-Type: application/json\" -d \'{{\"sessionKey\": \"your-session-key\"}}\'' if url else 'aws lambda get-function-url-config --function-name tq-lambda --query FunctionUrl --output text')" 2>/dev/null || echo "aws lambda get-function-url-config --function-name tq-lambda --query FunctionUrl --output text"

destroy:
	@cd $(INFRA_DIR) && (cdk destroy --force 2>/dev/null || npx -y aws-cdk destroy --force)

test: $(VENV_DIR)
	@$(VENV)/pip install -r $(LAMBDA_DIR)/requirements.txt --quiet
	@$(VENV)/pip install pytest --quiet
	@$(VENV)/pytest $(LAMBDA_DIR) $(INFRA_DIR) -v || true

$(VENV_DIR):
	@python3 -m venv $(VENV_DIR)
	@$(VENV)/pip install --upgrade pip --quiet

clean:
	@rm -rf $(BUILD_DIR) $(PACKAGE_NAME) cdk-outputs.json $(VENV_DIR)
	@find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
