package com.discovery.rag.ragdemo.controller;

import com.discovery.rag.ragdemo.service.RagService;
import org.springframework.ai.document.Document;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/rag")
public class RagController {

    private final RagService ragService;

    public RagController(RagService ragService) {
        this.ragService = ragService;
    }

    @GetMapping("/search")
    public List<SearchResult> search(@RequestParam("q") String question) {
        return ragService.searchInRag(question).stream()
                .map(SearchResult::from)
                .toList();
    }

    public record SearchResult(String id, String text, Map<String, Object> metadata, Double score) {
        static SearchResult from(Document document) {
            return new SearchResult(document.getId(), document.getText(), document.getMetadata(), document.getScore());
        }
    }
}
