import { FaChartArea } from 'react-icons/fa';
import './InsightCard.css';

const FormatInsight = ({ text }: { text: string }) => {
  const parts = text.split(/(\*\*.*?\*\*)/g);

  return (
    <p className="insight-text">
           
      {parts.map((part, i) =>
        part.startsWith('**') && part.endsWith('**') ? (
          <strong key={i}>{part.substring(2, part.length - 2)}</strong>
        ) : (
          <span key={i}>{part}</span>
        ),
      )}
         
    </p>
  );
};

type InsightCardProps = {
  insights: string[];
};

export function InsightCard({ insights }: InsightCardProps) {
  if (!insights || insights.length === 0) {
    return null;
  }

  return (
    <div className="insight-card-wrapper">
       
      <div className="insight-card">
               
        <div className="insight-header">
                   
          <span className="insight-icon">
                        <FaChartArea />         
          </span>
                    <h4 className="insight-title">Visão Geral de Desempenho</h4>
                 
        </div>
               
        <div className="insight-body">
                   
          {insights.map((insight, index) => (
            <FormatInsight key={index} text={insight} />
          ))}
                 
        </div>
             
      </div>
         
    </div>
  );
}
