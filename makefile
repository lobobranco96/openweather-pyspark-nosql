up:
	docker compose -f services/orchestration.yml -f services/applications.yml up -d
	
down:
	docker compose -f services/orchestration.yml -f services/applications.yml down

build:
	docker compose -f services/orchestration.yml -f services/applications.yml up -d --build