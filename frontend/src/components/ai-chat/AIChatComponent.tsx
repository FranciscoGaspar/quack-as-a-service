"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { useCustomAnalysis, useQuickAnswer } from "@/hooks/ai-analytics/useAIAnalytics";
import { BarChart3, Bot, MessageSquare, Send, User, Lightbulb, ChevronDown, ChevronRight } from "lucide-react";
import { useState } from "react";

// Suggested questions organized by category
const FACTORY_SAFETY_QUESTIONS = {
  "Compliance Overview": [
    "What's our overall safety compliance rate?",
    "How is our factory performing on safety standards?",
    "What are the main compliance issues today?",
    "Show me our current safety status"
  ],
  "Equipment Issues": [
    "Which safety equipment has the highest violation rate?",
    "Why do workers keep forgetting masks?",
    "How can we improve glove compliance?",
    "What PPE violations are most common?"
  ],
  "Room Performance": [
    "Which room has the worst safety performance?",
    "How does the production floor compare to packaging area?",
    "What are the safety issues in the assembly line?",
    "Which areas need immediate safety attention?"
  ],
  "Risk Assessment": [
    "What are our highest safety risks right now?",
    "Are there any critical safety violations?",
    "What safety problems need urgent action?",
    "Which areas pose the greatest safety danger?"
  ],
  "Time Patterns": [
    "What time of day has the worst compliance?",
    "How does safety performance vary by shift?",
    "Are there patterns in safety violations?",
    "When do most safety incidents occur?"
  ],
  "Worker Performance": [
    "Which workers have the most safety violations?",
    "Who are our highest risk workers?",
    "Which employees need additional safety training?",
    "How do individual workers compare on safety compliance?"
  ],
  "Training Needs": [
    "Which workers need immediate safety training?",
    "What training gaps exist in our workforce?",
    "How effective are our current training programs?",
    "Who should be prioritized for safety coaching?"
  ],
  "Recommendations": [
    "How can we improve our safety compliance?",
    "What training programs should we implement?",
    "How can we reduce safety violations?",
    "What are the best ways to improve factory safety?"
  ]
};

export const ChatComponent = () => {
  const [question, setQuestion] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [chatHistory, setChatHistory] = useState<Array<{
    id: string;
    type: 'user' | 'ai';
    content: string;
    timestamp: Date;
    analysisType?: 'quick' | 'detailed';
    questionCategory?: string;
  }>>([]);
  const [isLoading, setIsLoading] = useState(false);

  const quickAnswerMutation = useQuickAnswer();
  const customAnalysisMutation = useCustomAnalysis();

  // Helper function to determine question category
  const getQuestionCategory = (questionText: string): string => {
    for (const [category, questions] of Object.entries(FACTORY_SAFETY_QUESTIONS)) {
      if (questions.includes(questionText)) {
        return category;
      }
    }
    return 'Custom';
  };

  const handleSuggestedQuestion = (suggestedQuestion: string) => {
    setQuestion(suggestedQuestion);
    setShowSuggestions(false);
  };

  const handleQuickAnswer = async () => {
    if (!question.trim()) return;

    const questionCategory = getQuestionCategory(question);
    const userMessage = {
      id: Date.now().toString(),
      type: 'user' as const,
      content: question,
      timestamp: new Date(),
      questionCategory,
    };

    setChatHistory(prev => [...prev, userMessage]);
    setIsLoading(true);
    setShowSuggestions(false);

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
        questionCategory,
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

    const questionCategory = getQuestionCategory(question);
    const userMessage = {
      id: Date.now().toString(),
      type: 'user' as const,
      content: question,
      timestamp: new Date(),
      questionCategory,
    };

    setChatHistory(prev => [...prev, userMessage]);
    setIsLoading(true);
    setShowSuggestions(false);

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
        questionCategory,
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
    setShowSuggestions(true);
    setSelectedCategory(null);
    setQuestion("");
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
        <div className="flex-1 overflow-y-auto space-y-4 max-h-96 relative">
          {chatHistory.length === 0 && showSuggestions ? (
            <div className="text-center text-muted-foreground py-4">
              <div className="flex items-center justify-center mb-4">
                <Lightbulb className="h-8 w-8 mx-auto text-blue-500" />
                <span className="ml-2 text-lg font-semibold text-gray-700">Factory Safety Assistant</span>
              </div>
              <p className="mb-4 text-sm">Ask me anything about your factory safety compliance data</p>
              
              {/* Suggested Questions by Category */}
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {Object.entries(FACTORY_SAFETY_QUESTIONS).map(([category, questions]) => (
                  <div key={category} className="text-left">
                    <div 
                      className="flex items-center justify-between p-2 bg-gray-50 rounded-lg cursor-pointer hover:bg-gray-100"
                      onClick={() => setSelectedCategory(selectedCategory === category ? null : category)}
                    >
                      <span className="font-medium text-sm text-gray-700">{category}</span>
                      {selectedCategory === category ? 
                        <ChevronDown className="h-4 w-4 text-gray-500" /> : 
                        <ChevronRight className="h-4 w-4 text-gray-500" />
                      }
                    </div>
                    
                    {selectedCategory === category && (
                      <div className="mt-2 space-y-1 pl-4">
                        {questions.map((question, idx) => (
                          <button
                            key={idx}
                            onClick={() => handleSuggestedQuestion(question)}
                            className="block w-full text-left p-2 text-xs text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded border border-blue-200 hover:border-blue-300 transition-colors"
                          >
                            {question}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ) : chatHistory.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              <MessageSquare className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p className="mb-2">Ask questions about your factory safety compliance</p>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => setShowSuggestions(true)}
                className="mt-2"
              >
                <Lightbulb className="h-4 w-4 mr-2" />
                Show Suggested Questions
              </Button>
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
                      {message.questionCategory && message.questionCategory !== 'Custom' && (
                        <Badge variant="secondary" className="text-xs">
                          {message.questionCategory}
                        </Badge>
                      )}
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
          
          {/* Floating Suggestions Panel */}
          {chatHistory.length > 0 && showSuggestions && (
            <div className="absolute top-4 left-4 right-4 bg-white border border-gray-200 rounded-lg shadow-lg p-4 z-10 max-h-64 overflow-y-auto">
              <div className="flex items-center justify-between mb-3">
                <span className="font-semibold text-sm text-gray-700">Suggested Questions</span>
                <Button
                  onClick={() => setShowSuggestions(false)}
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0"
                >
                  ×
                </Button>
              </div>
              
              <div className="space-y-2">
                {Object.entries(FACTORY_SAFETY_QUESTIONS).map(([category, questions]) => (
                  <div key={category}>
                    <div 
                      className="flex items-center justify-between p-1 cursor-pointer hover:bg-gray-50 rounded"
                      onClick={() => setSelectedCategory(selectedCategory === category ? null : category)}
                    >
                      <span className="font-medium text-xs text-gray-600">{category}</span>
                      {selectedCategory === category ? 
                        <ChevronDown className="h-3 w-3 text-gray-400" /> : 
                        <ChevronRight className="h-3 w-3 text-gray-400" />
                      }
                    </div>
                    
                    {selectedCategory === category && (
                      <div className="ml-2 space-y-1">
                        {questions.map((question, idx) => (
                          <button
                            key={idx}
                            onClick={() => {
                              handleSuggestedQuestion(question);
                              setShowSuggestions(false);
                            }}
                            className="block w-full text-left p-1 text-xs text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors"
                          >
                            {question}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
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
          
          <div className="flex gap-2 justify-between">
            <div className="flex gap-2">
              {chatHistory.length > 0 && !showSuggestions && (
                <Button
                  onClick={() => setShowSuggestions(true)}
                  variant="ghost"
                  size="sm"
                  className="text-xs"
                >
                  <Lightbulb className="h-4 w-4 mr-1" />
                  Suggestions
                </Button>
              )}
            </div>
            
            <div className="flex gap-2">
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
        </div>
      </CardContent>
    </Card>
  );
};
