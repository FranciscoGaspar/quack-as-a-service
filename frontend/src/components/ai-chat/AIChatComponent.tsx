"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { useCustomAnalysis, useQuickAnswer } from "@/hooks/ai-analytics/useAIAnalytics";
import { BarChart3, Bot, MessageSquare, Send, User } from "lucide-react";
import { useState } from "react";

export const ChatComponent = () => {
  const [question, setQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState<Array<{
    id: string;
    type: 'user' | 'ai';
    content: string;
    timestamp: Date;
    analysisType?: 'quick' | 'detailed';
  }>>([]);
  const [isLoading, setIsLoading] = useState(false);

  const quickAnswerMutation = useQuickAnswer();
  const customAnalysisMutation = useCustomAnalysis();

  const handleQuickAnswer = async () => {
    if (!question.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      type: 'user' as const,
      content: question,
      timestamp: new Date(),
    };

    setChatHistory(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await quickAnswerMutation.mutateAsync({
        question: question.trim(),
        limit: 50
      });

      const aiMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai' as const,
        content: response.answer,
        timestamp: new Date(),
        analysisType: 'quick' as const,
      };

      setChatHistory(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai' as const,
        content: `Sorry, I couldn't process your question. Please try again.`,
        timestamp: new Date(),
        analysisType: 'quick' as const,
      };

      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setQuestion("");
    }
  };

  const handleDetailedAnalysis = async () => {
    if (!question.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      type: 'user' as const,
      content: question,
      timestamp: new Date(),
    };

    setChatHistory(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await customAnalysisMutation.mutateAsync({
        userPrompt: question.trim(),
        limit: 100
      });

      const analysis = response.analysis;
      const aiMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai' as const,
        content: `${analysis?.summary || 'Analysis completed'}\n\nKey Findings:\n${analysis?.key_findings?.map(f => `• ${f}`).join('\n') || 'No findings'}\n\nRecommendations:\n${analysis?.recommendations?.map(r => `• ${r}`).join('\n') || 'No recommendations'}`,
        timestamp: new Date(),
        analysisType: 'detailed' as const,
      };

      setChatHistory(prev => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai' as const,
        content: `Sorry, I couldn't perform the detailed analysis. Please try again.`,
        timestamp: new Date(),
        analysisType: 'detailed' as const,
      };

      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setQuestion("");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleQuickAnswer();
    }
  };

  const clearChat = () => {
    setChatHistory([]);
  };

  return (
    <Card className="h-[600px] flex flex-col">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5 text-blue-600" />
            Ask AI About Your Data
          </div>
          <Button onClick={clearChat} variant="outline" size="sm">
            Clear Chat
          </Button>
        </CardTitle>
      </CardHeader>
      
      <CardContent className="flex-1 flex flex-col space-y-4">
        {/* Chat History */}
        <div className="flex-1 overflow-y-auto space-y-4 max-h-96">
          {chatHistory.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              <MessageSquare className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p className="mb-2">Ask questions about your compliance data</p>
              <p className="text-sm">Try: "What are the main compliance issues?" or "Which room has the worst performance?"</p>
            </div>
          ) : (
            chatHistory.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex gap-3 ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    message.type === 'user' 
                      ? 'bg-blue-600 text-white' 
                      : 'bg-purple-600 text-white'
                  }`}>
                    {message.type === 'user' ? (
                      <User className="h-4 w-4" />
                    ) : (
                      <Bot className="h-4 w-4" />
                    )}
                  </div>
                  <div className={`max-w-[80%] ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
                    <div className={`rounded-lg p-3 ${
                      message.type === 'user'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                      <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    </div>
                    <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                      <span>{message.timestamp.toLocaleTimeString()}</span>
                      {message.analysisType && (
                        <Badge variant="outline" className="text-xs">
                          {message.analysisType === 'quick' ? 'Quick Answer' : 'Detailed Analysis'}
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-600 text-white flex items-center justify-center">
                <Bot className="h-4 w-4" />
              </div>
              <div className="bg-gray-100 rounded-lg p-3">
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
                  <span className="text-sm text-gray-600">AI is thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="space-y-3">
          <div className="flex gap-2">
            <Textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about your compliance data..."
              className="flex-1 min-h-[60px] resize-none"
              disabled={isLoading}
            />
          </div>
          
          <div className="flex gap-2 justify-end">
            <Button
              onClick={handleDetailedAnalysis}
              disabled={!question.trim() || isLoading}
              variant="outline"
              size="sm"
            >
              <BarChart3 className="h-4 w-4 mr-2" />
              Detailed Analysis
            </Button>
            <Button
              onClick={handleQuickAnswer}
              disabled={!question.trim() || isLoading}
              size="sm"
            >
              <Send className="h-4 w-4 mr-2" />
              Quick Answer
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
