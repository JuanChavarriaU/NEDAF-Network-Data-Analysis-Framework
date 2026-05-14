import { useState, useRef, useEffect } from 'react';
import { Bot, Send, User, Loader2, Sparkles, BrainCircuit } from 'lucide-react';
import { AI_API, handleApiError } from './services/api';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  isError?: boolean;
}

export function LLMInsights() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: '¡Hola! Soy tu asistente de grafos basado en Phi-3-Mini. Puedo analizar las métricas de tu dataset y red, y darte insights estadísticos u orientarte teóricamente en el análisis de redes complejas. ¿En qué puedo ayudarte hoy?',
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setInput('');
    
    // Add user message to UI
    const newMessageId = Date.now().toString();
    setMessages(prev => [...prev, { id: newMessageId, role: 'user', content: userMsg }]);
    
    setIsLoading(true);

    try {
      const response = await AI_API.getInsights({ 
        question: userMsg,
        include_graph_metrics: true
      });
      
      setMessages(prev => [
        ...prev, 
        { 
          id: (Date.now() + 1).toString(), 
          role: 'assistant', 
          content: response.response 
        }
      ]);
    } catch (error) {
      const errorMsg = handleApiError(error);
      setMessages(prev => [
        ...prev, 
        { 
          id: (Date.now() + 1).toString(), 
          role: 'assistant', 
          content: `**Error:** ${errorMsg}\n\n*Asegúrate de que Ollama está corriendo en el backend.*`,
          isError: true
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full animate-fade-in fade-in zoom-in duration-300">
      <header className="glass-panel mb-4 p-5 flex items-center justify-between relative z-20">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <BrainCircuit className="text-brand-400" />
            LLM Insights (Modo Offline)
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Analiza la topología y estadísticas de tu grafo con IA local sin enviar datos a la nube.
          </p>
        </div>
        <div className="flex items-center gap-2 bg-brand-500/20 text-brand-300 px-3 py-1.5 rounded-full border border-brand-500/30 text-xs font-semibold">
          <Sparkles size={14} />
          Modelo: Phi-3-Mini
        </div>
      </header>

      <div className="flex-1 glass-panel overflow-hidden flex flex-col relative bg-dark-bg/30">
        <div className="absolute inset-0 pattern-grid opacity-5 pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)', backgroundSize: '32px 32px' }} />
        
        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-4 md:p-6 custom-scrollbar space-y-6 relative z-10">
          {messages.map((msg) => (
            <div 
              key={msg.id} 
              className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`flex gap-3 max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                  msg.role === 'user' ? 'bg-brand-500' : 'bg-indigo-600'
                }`}>
                  {msg.role === 'user' ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
                </div>

                <div className={`p-4 rounded-2xl ${
                  msg.role === 'user' 
                    ? 'bg-brand-600/90 text-white rounded-tr-sm border border-brand-500/50' 
                    : msg.isError 
                      ? 'bg-red-900/40 text-red-100 rounded-tl-sm border border-red-500/50'
                      : 'bg-dark-panel text-gray-200 rounded-tl-sm border border-dark-border shadow-lg shadow-black/20'
                }`}>
                  <div className="prose prose-invert prose-sm max-w-none">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                </div>

              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex w-full justify-start">
              <div className="flex gap-3 max-w-[80%] flex-row">
                <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center shrink-0">
                  <Bot size={16} className="text-white" />
                </div>
                <div className="p-4 rounded-2xl bg-dark-panel text-gray-200 rounded-tl-sm border border-dark-border flex items-center gap-2">
                  <Loader2 className="animate-spin text-brand-400" size={18} />
                  <span className="text-sm text-gray-400">Analizando contexto del grafo...</span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-dark-bg/80 border-t border-dark-border backdrop-blur-md relative z-20">
          <form onSubmit={handleSubmit} className="flex items-center gap-3 max-w-4xl mx-auto">
            <div className="relative flex-1">
              <input 
                type="text" 
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Pregúntale al SLM sobre componentes conexos, modularidad, hubs..."
                className="w-full bg-dark-panel border border-dark-border rounded-xl pl-4 pr-12 py-3.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-brand-500 transition-colors shadow-inner"
                disabled={isLoading}
              />
            </div>
            <button 
              type="submit" 
              disabled={isLoading || !input.trim()}
              className="bg-brand-600 hover:bg-brand-500 disabled:opacity-50 disabled:hover:bg-brand-600 text-white p-3.5 rounded-xl transition-colors shadow-lg shadow-brand-900/20 shrink-0"
            >
              <Send size={18} className={input.trim() && !isLoading ? 'translate-x-0.5 -translate-y-0.5 transition-transform' : ''} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
