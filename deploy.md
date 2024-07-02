# Deployment guide

## Local

Prerequisites:

- Python 3.9
- PostgreSQL database
- Redis

Install required packages:

```bash
pip install -r requirements.txt
```

Update environment configuration:

- Rename `.env.example` to `.env`
- Update the newly-created `.env`:

    ```bash
    DB_NAME=<uri to your postgresql database>
    CACHE_TYPE=RedisCache
    CACHE_REDIS_URL=<uri to your redis database>
    MAX_TABLE=<maximum dine-in tables of a restaurant>
    MAX_TABLE_PER_ROW=<maximum dine-in tables per row>
    PINCODE=<your choice - 6 digits>
    SECRET_KEY=<your choice>
    MAX_BESTSELLER_RECOMMEND=<maximum best items to recommend to a new user>
    POSTGRES_USER=<postgres user (before :)>
    POSTGRES_PASSWORD=<postgres password (between : and @)>
    POSTGRES_DB=<postgres db (last parameter)>
    ```

Initialize database

```bash
flask --app run init-db
```

Run

```bash
bash run.sh
```

Note: to run on external IP, use `entrypoint.sh`

```bash
bash entrypoint.sh
```

## Docker

The official Docker image of AIAOs-KDS can be found [here](https://hub.docker.com/r/trhgquan/aiaos-kds)

### Build Docker image

Update environment configuration:

- Rename `.env.docker.example` to `.env`
- Update the newly-created `.env`:

```bash
DB_NAME=<uri to your postgresql database>
CACHE_TYPE=RedisCache
CACHE_REDIS_URL=<uri to your redis database>
MAX_TABLE=<maximum dine-in tables of a restaurant>
MAX_TABLE_PER_ROW=<maximum dine-in tables per row>
PINCODE=<your choice - 6 digits>
SECRET_KEY=<your choice>
MAX_BESTSELLER_RECOMMEND=<maximum best items to recommend to a new user>
POSTGRES_USER=<postgres user (before :)>
POSTGRES_PASSWORD=<postgres password (between : and @)>
POSTGRES_DB=<postgres db (last parameter)>
```

Build Docker image:

```bash
docker build -t aiaos-kds/<tag>:version
```

Run:

Update docker image name to the `web` service in `docker-compose.yaml`:

```yaml
web:
    container_name: AIAOs-KDS
    image: <image name goes here>
```

Then, run the server!

```bash
docker-compose up
```

### Run Docker image from Dockerhub

Pull the `trhgquan/aiaos-kds:latest` image:

```bash
docker image pull trhgquan/aiaos-kds:latest
```

Then run:

```bash
docker-compose up
```

## Render

### Environment setup (for deploying with GitHub)

| Field          | Value                                           |
| -------------- | ----------------------------------------------- |
| Branch         | `deploy` (`main` by default)                    |
| Root Directory | leave it blank                                  |
| Build Command  | `pip install -r requirements.txt`               |
| Start Command  | `gunicorn --worker-class eventlet -w 1 run:app` |
| Auto-Deploy    | `Yes`                                           |

### Environment setup (for deploying with Docker image)

| Field      | Value             |
| ---------- | ----------------- |
| Entrypoint | `./entrypoint.sh` |

## Database setup

1. You might want to create accounts and have permissions set up on the storage manager. This is not required, yet still necessary for further actions.
2. Please change the postgres database datetime format to `ISO, DMY`:

    ```sql
    ALTER DATABASE "my_database_name" SET datestyle TO "ISO, DMY";
    ```

    The detailed guide can be found [here](https://dba.stackexchange.com/a/126911)

3. Connect to database using the postgres uri.
4. Run `flask --app run init-db` to init the database.
5. Login to the deployment web and update environment `db_name`.

## Redis setup

Create a Redis instance, then use its URL.

### Environment Variables setup

| Field               | Value                                                                                                                          |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `MAX_TABLE`         | maximum dine-in tables of a restaurant                                                                                         |
| `MAX_TABLE_PER_ROW` | maximum dine-in tables per row (dine-in only)                                                                                  |
| `DB_NAME`           | **internal** uri of the Postgres database                                                                                      |
| `CACHE_TYPE`        | `RedisCache`                                                                                                                   |
| `CACHE_REDIS_URL`   | uri of the redis service                                                                                                       |
| `PINCODE`           | your choice - 6 digits                                                                                                         |
| `SECRET_KEY`        | (Optional) your self modified secret key                                                                                       |
| `MAX_BESTSELLER_RECOMMEND` | (Optional) maximum items to recommend to a new user |
| `TIMEZONE`          | (Optional) Default is `Asia/Ho_Chi_Minh`, [view list of timezone here](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568) |
