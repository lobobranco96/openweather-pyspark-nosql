up:
	docker compose -f services/orchestration.yml -f services/applications.yml -f services/visualization.yml up -d

down:
	docker compose -f services/orchestration.yml -f services/applications.yml -f services/visualization.yml down

build:
	docker compose -f services/orchestration.yml -f services/applications.yml up -f services/visualization.yml up -d --build

streamlit:
	docker compose -f services/visualization.yml up -d