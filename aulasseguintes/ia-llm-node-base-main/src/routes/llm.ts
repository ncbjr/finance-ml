import express from 'express';
import {
    createOpenAIClient,
    createAnthropicClient,
    createXAIClient,
    createGoogleClient,
    createGroqClient,
    createOllamaClient
} from '../services/index.js';

const router = express.Router();

// Route para OpenAI
router.get('/openai', async (req, res) => {
    const client = createOpenAIClient();
    res.json({
        provider: 'OpenAI',
        message: 'Cliente OpenAI criado com sucesso',
        client: !!client
    });
});

// Route para Anthropic (Claude)
router.get('/anthropic', async (req, res) => {
    const client = createAnthropicClient();
    res.json({
        provider: 'Anthropic (Claude)',
        message: 'Cliente Anthropic criado com sucesso',
        client: !!client
    });
});

// Route para xAI (Grok)
router.get('/xai', async (req, res) => {
    const client = createXAIClient();
    res.json({
        provider: 'xAI (Grok)',
        message: 'Cliente xAI criado com sucesso',
        client: !!client
    });
});

// Route para Google AI (Gemini)
router.get('/google', async (req, res) => {
    const client = createGoogleClient();
    res.json({
        provider: 'Google AI (Gemini)',
        message: 'Cliente Google AI criado com sucesso',
        client: !!client
    });
});

// Route para Groq
router.get('/groq', async (req, res) => {
    const client = createGroqClient();
    res.json({
        provider: 'Groq',
        message: 'Cliente Groq criado com sucesso',
        client: !!client
    });
});

// Route para Ollama
router.get('/ollama', async (req, res) => {
    const client = createOllamaClient();
    res.json({
        provider: 'Ollama',
        message: 'Cliente Ollama criado com sucesso',
        client: !!client
    });
});

export default router;