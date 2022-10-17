# TestCase01
Чтобы запустить сервис клонируйте репозиторий в подготовленную папку
командой:

__git clone https://github.com/vic-k23/TestCase01.git__

Перейдите в склонированный каталог и создайте docker-образ командой:

__docker build -t myservice .__

Затем запустите сервис командой:

__docker run -p 80:80 --rm -d myservice__

По адресу http://localhost/docs станет доступен интерфейс openapi/swagger ui
