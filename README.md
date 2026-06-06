# Развертывание и Наблюдаемость Приложения в Kubernetes (Лаб. №5, 6, 7)

Этот репозиторий содержит все необходимые файлы для развертывания и мониторинга приложения в локальном кластере Kubernetes (например, в Docker Desktop).

Проект демонстрирует итеративное развитие от простого развертывания к профессиональной IaC-структуре с наблюдаемостью.

## Пререквизиты

*   Установлен Docker Desktop с включенным Kubernetes.
*   Установлен `kubectl`.
*   Установлен `helm`.
*   Установлен Git.

---

## Лабораторная работа №7: Observability (Prometheus, Grafana)

Этот раздел описывает, как развернуть приложение вместе со стеком мониторинга для сбора и визуализации метрик.

### Как запустить (с нуля)

**1. Переключитесь на ветку `lab7`:**
```bash
git checkout lab7
```

**2. Соберите финальный Docker-образ:**
```bash
docker build -t lab-app:v17 .
```
*(Убедитесь, что в файле `k8s/app/kustomization/base/app-services.yaml` используется именно этот тег).*

**3. Установите стек наблюдаемости (Prometheus & Grafana):**
*   Сначала добавьте репозиторий Helm:
    ```bash
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    ```
*   Затем установите `kube-prometheus-stack` в отдельный неймспейс `observability`:
    ```bash
    helm install prometheus prometheus-community/kube-prometheus-stack --namespace observability --create-namespace
    ```
    *(Установка может занять несколько минут).*

**4. Разверните инфраструктуру (PostgreSQL):**
```bash
kubectl kustomize k8s/infra/kustomization/overlays/dev | kubectl apply -f -
```

**5. Дождитесь готовности базы данных:**
```bash
# Ждите, пока под postgres-0 не перейдет в статус Running и READY 1/1
kubectl get pods -n lab6-dev -w
```

**6. Разверните приложение:**
```bash
kubectl kustomize k8s/app/kustomization/overlays/dev | kubectl apply -f -
```
*На этом шаге будет создан `ServiceMonitor`, который автоматически настроит Prometheus на сбор метрик с `user-service`.*

**7. Настройте доступ и проверьте:**
*   Добавьте строку `127.0.0.1 app.lab6.local` в ваш файл `hosts`.
*   Откройте в браузере [http://app.lab6.local](http://app.lab6.local). Вы должны увидеть `{"message":"Service is running with Prometheus metrics!"}`.

### Проверка метрик и дашборда

#### 1. Проверка Prometheus

1.  Пробросьте порт для доступа к Prometheus UI:
    ```bash
    kubectl port-forward svc/prometheus-operated 9090:9090 -n observability
    ```
2.  Откройте `http://localhost:9090` в браузере.
3.  Перейдите в меню **Status -> Targets**. Вы должны увидеть цель для `user-service` в состоянии **UP**.

**Скриншот №1: Prometheus Targets**
![Prometheus Targets](docs/screenshots/lab7/Screenshot%20from%202026-05-29%2018-02-45.png)


#### 2. Проверка Grafana

1.  Получите пароль администратора Grafana:
    ```bash
    kubectl get secret prometheus-grafana -n observability -o jsonpath="{.data.admin-password}" | base64 --decode
    ```
2.  Пробросьте порт для доступа к Grafana:
    ```bash
    kubectl port-forward svc/prometheus-grafana 3000:80 -n observability
    ```
3.  Зайдите на `http://localhost:3000` (логин `admin`, пароль — полученный выше).
4.  Создайте новый дашборд и панель с запросом PromQL, например `rate(http_requests_total{job="user-service-monitor/0"}[5m])`.
5.  Создайте нагрузку (`while true; do curl http://app.lab6.local/; done`), чтобы на графике появились данные.

**Скриншот №2: Дашборд Grafana**

![Grafana Dashboard](docs/screenshots/lab7/Screenshot%20from%202026-05-29%2002-08-49.png)

#### 3. Проверка распределенного трейсинга в Tempo

1.  В Grafana перейдите в **Connections -> Data sources -> Add new data source**. Выберите **Tempo** и в поле URL укажите `http://tempo.observability:3200`. Нажмите **Save & test**.
2.  Сделайте несколько запросов к приложению, чтобы сгенерировать трейсы:
    ```bash
    curl http://app.lab6.local/
    ```
3.  В Grafana перейдите в раздел **Explore** (иконка компаса) и выберите источник данных **Tempo**.
4.  Нажмите **Run query**. В результатах должен появиться трейс от `user-service`.

**Скриншот №3: Трейс в Grafana Tempo**


![Tempo Trace](docs/screenshots/lab7/Screenshot%20from%202026-06-06%2020-23-40.png)

### Очистка

Чтобы удалить все созданные ресурсы, выполните:
```bash
kubectl delete namespace lab6-dev
helm uninstall prometheus -n observability
helm uninstall tempo -n observability
kubectl delete namespace observability
```
