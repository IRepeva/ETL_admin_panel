docker_app = docker-compose exec app
manage =  python manage.py

make_migrations:
	@echo "Creating migrations..."
	@${docker_app} ${manage} makemigrations
	@echo "Migrations were created"

migrate:
	@echo "Applying migrating..."
	@${docker_app} ${manage} migrate --noinput
	@echo "All migrations are applied"

collect_static:
	@echo "Collecting static..."
	@${docker_app} ${manage} collectstatic --noinput
	@echo "Static collection is finished"

fill_db:
	@echo "Filling database with data..."
	@${docker_app} python ../deploy/postgres/fill_db/load_data.py
	@echo "Data was transferred to database"

create_superuser:
	@echo "Creating superuser..."
	@${docker_app} ${manage} createsuperuser --noinput
	@echo "Superuser was created"
