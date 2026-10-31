package com.discovery.rag.ragdemo.service;

import org.springframework.ai.document.Document;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class RagService {

    private final VectorStore vectorStore;

    @Autowired
    public RagService(VectorStore vectorStore) {
        this.vectorStore = vectorStore;
    }

    public List<Document> searchInRag(String text) {
        return this.vectorStore.similaritySearch(SearchRequest.builder().query(text).topK(5).build());
    }
}
