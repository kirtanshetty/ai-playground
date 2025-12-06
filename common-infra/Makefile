.PHONY: deploy destroy init

init:
	@pip3 install -r requirements.txt --quiet
	@npx -y cdktf-cli@latest get

deploy: init
	@npx -y cdktf-cli@latest deploy --auto-approve

destroy:
	@npx -y cdktf-cli@latest destroy --auto-approve
