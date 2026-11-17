# Docker and PostgreSQL Command Reference

## Docker commands

| Command | Purpose |
|---|---|
| docker version | Check Docker version |
| docker pull postgres:17 | Download PostgreSQL image |
| docker images | List images |
| docker run -d ... | Create and start a container |
| docker ps | List running containers |
| docker ps -a | List all containers |
| docker logs pg | Display container logs |
| docker logs -f pg | Follow container logs |
| docker exec -it pg bash | Open container shell |
| docker inspect pg | Inspect container configuration |
| docker stop pg | Stop container |
| docker start pg | Start container |
| docker rm pg | Remove container |
| docker volume ls | List volumes |
| docker network ls | List networks |
| docker system df | Check Docker disk usage |
| docker build -t app:release-a . | Build an image |
| docker exec pg pg_isready | Check PostgreSQL readiness |

## PostgreSQL psql commands

| Command | Purpose |
|---|---|
| \l | List databases |
| \c database_name | Connect to a database |
| \dt | List tables |
| \d table_name | Describe a table |
| \x | Toggle expanded output |
| \i filename.sql | Execute SQL file |
| \? | Show psql command help |
| \q | Quit psql |

## SQL commands

| Command | Purpose |
|---|---|
| SELECT | Retrieve records |
| WHERE | Filter records |
| ORDER BY | Sort records |
| LIMIT | Limit output |
| COUNT() | Count records |
| GROUP BY | Group records |
| HAVING | Filter grouped results |
| INNER JOIN | Retrieve matching records |
| LEFT JOIN | Retain all left-side records |
| IS NULL | Find missing matches |
| SUM() | Calculate totals |
| RANK() | Rank records |
| ROW_NUMBER() | Assign sequential row numbers |
| WITH | Define a CTE |
| EXPLAIN | View query execution plan |
| CREATE INDEX | Create an index |
| ON CONFLICT | Handle duplicate-key conflicts |