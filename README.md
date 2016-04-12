# GitHub Charon - Pull Request Validation Tool

## Installation

- Install Docker on your machine (see <https://get.docker.com/> or <https://docs.docker.com/installation/>).
- `git clone https://github.com/skies-io/GitHub-Charon.git`
- `docker build -t charon GitHub-Charon/`
- `docker run --name charon -p 5000:5000 -d charon`
- Configure the application by visiting its home page


## Access

You can access this website through `http://your-domain.tld:5000`.

If you want to use port 80, run your image with this command: `docker run --name charon -p 80:5000 -d charon`.

Otherwise, if you want use Nginx or Apache, here is their configurations:

### Nginx

```
upstream charon {
    server 127.0.0.1:5000;
}
server {
    listen 80;
    server_name your-domain.tld;
    location / {
        proxy_pass http://charon;
    }
}
```

### Apache

Beforehand, you must enable modules `proxy` and `proxy_http`.

```
<VirtualHost your-domain.tld:80>
        ServerName your-domain.tld
        ProxyPass / http://localhost:5000/
        ProxyPassReverse / http://localhost:5000/
        ProxyPreserveHost On
</VirtualHost>
```
