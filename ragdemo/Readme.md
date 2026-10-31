# RAG with SpringBoot

## Start

```shell
./gradlew bootRun
```

## Call RAG

```shell
curl -G http://localhost:8080/rag/search --data-urlencode "q=Quel est le port de pêche principal ?"
```

![search-with-springboot.png](../assets/search-with-springboot.png)

