init-env:
	brew install pyenv pyenv-virtualenv
	eval "$(pyenv init-)"
	eval "$(pyenv virtualenv-init -)";  
	export PATH="$HOME/.pyenv/bin:$PATH"
	pyenv install 3.9
	pyenv virtualenv 3.9 cuya-courts

env:
	pyenv activate cuya-courts

init-db:
	python scripts/init_db.py

image-local:
	docker build -t case-scrape-local .
	docker run -p 9000:8080 case-scrape-local:latest

image-test-local:
	curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{"case_number":"655783"}'

update-ecr-image:
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 952753501735.dkr.ecr.us-east-1.amazonaws.com
	docker build -t case-scrape .
	docker tag case-scrape:latest 952753501735.dkr.ecr.us-east-1.amazonaws.com/case-scrape:latest
	docker push 952753501735.dkr.ecr.us-east-1.amazonaws.com/case-scrape:latest
	
update-lambda:
	aws lambda update-function-code --function-name case-scrape --image-uri 952753501735.dkr.ecr.us-east-1.amazonaws.com/case-scrape:latest

pg-dump-from-aws:
	pg_dump -Z 9 -v -h ${DATABASE_HOST} -U ${DATABASE_USER} -d ${DATABASE_NAME} | aws s3 cp --storage-class STANDARD --sse aws:kms - s3://my-bucket/dump.sql.gz

