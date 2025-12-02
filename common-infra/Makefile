.PHONY: deploy destroy init

init:
	@pip3 install -r requirements.txt --quiet
	@cdktf get

deploy: init
	@cdktf deploy --auto-approve

destroy:
	@cdktf destroy --auto-approve
