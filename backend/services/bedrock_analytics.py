"""
AWS Bedrock-powered NLP Analytics Service for Compliance Data
Generates intelligent insights using AWS Bedrock models (Claude, Titan, etc.)

This is the primary AI analytics service for the compliance tracking system.
OpenAI dependencies have been removed in favor of AWS Bedrock for better
enterprise integration, cost control, and model flexibility.
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# AWS Bedrock Dependencies
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BEDROCK_AVAILABLE = True
    print("✅ AWS Bedrock library loaded")
except ImportError as e:
    print(f"⚠️  AWS Bedrock library not available: {e}")
    print("💡 Install with: pip install boto3")
    BEDROCK_AVAILABLE = False

from database.services import PersonalEntryService
from database.models import PersonalEntry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AIInsight:
    """AI-generated insight using AWS Bedrock."""
    insight_type: str
    title: str
    summary: str
    detailed_analysis: str
    key_findings: List[str]
    recommendations: List[str]
    risk_level: str
    confidence_score: float
    generated_at: datetime
    data_period: str
    model_used: str

@dataclass
class ComplianceReport:
    """Comprehensive AI-generated compliance report."""
    executive_summary: str
    compliance_overview: Dict[str, Any]
    trend_analysis: str
    risk_assessment: str
    action_items: List[Dict[str, str]]
    insights: List[AIInsight]
    generated_at: datetime
    model_used: str

class BedrockNLPanalytics:
    """AWS Bedrock-powered NLP Analytics for compliance data."""
    
    def __init__(self, region_name: str = "us-east-1", model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"):
        self.bedrock_client = None
        self.is_initialized = False
        self.region_name = region_name
        self.model_id = model_id
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        
        
        # Equipment labels for better context
        self.equipment_labels = {
            'mask': 'Face Mask',
            'hairnet': 'Hair Net',
            'hard_hat': 'Hard Hat',
            'gloves': 'Gloves',
            'safety_glasses': 'Safety Glasses'
        }
        
        # Initialize Bedrock client
        self._initialize_bedrock()
    
    def _initialize_bedrock(self):
        """Initialize AWS Bedrock client."""
        if not BEDROCK_AVAILABLE:
            logger.warning("AWS Bedrock library not available")
            return

        if not self.aws_access_key_id or not self.aws_secret_access_key:
            logger.error("❌ AWS credentials not found. Please configure AWS credentials.")
            return
        
        try:
            # Initialize Bedrock client
            self.bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
            
            # Test the connection
            self._test_bedrock_connection()
            
            self.is_initialized = True
            logger.info(f"✅ AWS Bedrock client initialized successfully (Region: {self.region_name}, Model: {self.model_id})")
            
        except NoCredentialsError:
            logger.error("❌ AWS credentials not found. Please configure AWS credentials.")
            self.is_initialized = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize AWS Bedrock client: {e}")
            self.is_initialized = False
    
    def _test_bedrock_connection(self):
        """Test Bedrock connection by listing available models."""
        try:
            # Test with a simple request directly using bedrock_client
            if not self.bedrock_client:
                raise Exception("Bedrock client not created")
                
            test_prompt = "Hello, this is a test."
            
            # Use Titan format for Titan models
            if "titan" in self.model_id.lower():
                body = {
                    "inputText": test_prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": 10,
                        "temperature": 0.3
                    }
                }
            else:
                # Use Claude format for Claude models
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": test_prompt}]
                }
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType='application/json'
            )
            
            logger.info("✅ Bedrock connection test successful")
        except Exception as e:
            logger.error(f"❌ Bedrock connection test failed: {e}")
            raise
    
    def _invoke_model(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.3) -> str:
        """Invoke the Bedrock model with the given prompt."""
        if not self.is_initialized or not self.bedrock_client:
            raise Exception("Bedrock client not initialized")
        
        try:
            # Prepare the request body based on model type
            if "claude" in self.model_id.lower():
                # Claude models use different format
                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            elif "titan" in self.model_id.lower():
                # Titan models format
                body = {
                    "inputText": prompt,
                    "textGenerationConfig": {
                        "maxTokenCount": max_tokens,
                        "temperature": temperature,
                        "topP": 0.9
                    }
                }
            elif "llama" in self.model_id.lower():
                # Llama models format
                body = {
                    "prompt": prompt,
                    "max_gen_len": max_tokens,
                    "temperature": temperature,
                    "top_p": 0.9
                }
            else:
                # Default format
                body = {
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            
            # Invoke the model
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json'
            )
            
            # Parse response based on model type
            response_body = json.loads(response['body'].read())
            
            if "claude" in self.model_id.lower():
                return response_body['content'][0]['text']
            elif "titan" in self.model_id.lower():
                return response_body['results'][0]['outputText']
            elif "llama" in self.model_id.lower():
                return response_body['generation']
            else:
                return response_body.get('completion', str(response_body))
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'AccessDeniedException':
                raise Exception(f"Access denied to Bedrock model {self.model_id}. Please check IAM permissions.")
            elif error_code == 'ValidationException':
                raise Exception(f"Invalid request to Bedrock model {self.model_id}: {e}")
            else:
                raise Exception(f"Bedrock API error: {e}")
        except Exception as e:
            raise Exception(f"Failed to invoke Bedrock model: {e}")
    
    async def generate_compliance_insights(self, entries: List[PersonalEntry], insight_type: str = "comprehensive") -> AIInsight:
        """Generate AI-powered compliance insights using AWS Bedrock."""
        if not self.is_initialized or not self.bedrock_client:
            return self._create_fallback_insight("AWS Bedrock not available")
        
        try:
            # Prepare data for analysis
            analysis_data = self._prepare_analysis_data(entries)
            
            # Create prompt for Bedrock
            prompt = self._create_analysis_prompt(analysis_data, insight_type)
            
            # Call Bedrock API
            ai_response = self._invoke_model(prompt, max_tokens=1500, temperature=0.3)
            
            # Extract structured insights
            insight = self._parse_ai_response(ai_response, analysis_data, insight_type)
            
            logger.info("✅ AI insights generated successfully using AWS Bedrock")
            return insight
            
        except Exception as e:
            logger.error(f"❌ Failed to generate AI insights: {e}")
            return self._create_fallback_insight(f"Error: {str(e)}")
    
    async def generate_executive_report(self, entries: List[PersonalEntry]) -> ComplianceReport:
        """Generate comprehensive executive report using AWS Bedrock."""
        if not self.is_initialized or not self.bedrock_client:
            return self._create_fallback_report("AWS Bedrock not available")
        
        try:
            # Prepare comprehensive data
            analysis_data = self._prepare_analysis_data(entries)
            
            # Create executive report prompt
            prompt = self._create_executive_report_prompt(analysis_data)
            
            # Call Bedrock API
            ai_response = self._invoke_model(prompt, max_tokens=2000, temperature=0.2)
            
            # Extract structured report
            report = self._parse_executive_report(ai_response, analysis_data)
            
            logger.info("✅ Executive report generated successfully using AWS Bedrock")
            return report
            
        except Exception as e:
            logger.error(f"❌ Failed to generate executive report: {e}")
            return self._create_fallback_report(f"Error: {str(e)}")
    
    async def generate_custom_analysis(self, entries: List[PersonalEntry], user_prompt: str) -> AIInsight:
        """Generate AI analysis based on user's custom prompt/question."""
        if not self.is_initialized or not self.bedrock_client:
            return self._create_fallback_insight("AWS Bedrock not available")
        
        try:
            # Prepare data for analysis
            analysis_data = self._prepare_analysis_data(entries)
            
            # Create custom prompt for user's question
            prompt = self._create_custom_analysis_prompt(analysis_data, user_prompt)
            
            # Call Bedrock API
            ai_response = self._invoke_model(prompt, max_tokens=2000, temperature=0.3)
            
            # Extract structured insights
            insight = self._parse_custom_response(ai_response, analysis_data, user_prompt)
            
            logger.info("✅ Custom AI analysis generated successfully using AWS Bedrock")
            return insight
            
        except Exception as e:
            logger.error(f"❌ Failed to generate custom AI analysis: {e}")
            return self._create_fallback_insight(f"Error: {str(e)}")
    
    async def generate_quick_answer(self, entries: List[PersonalEntry], question: str) -> str:
        """Generate a quick answer to a user's question about compliance data."""
        if not self.is_initialized or not self.bedrock_client:
            return "AI service not available. Please check AWS Bedrock configuration."
        
        try:
            # Prepare basic data
            analysis_data = self._prepare_analysis_data(entries)
            
            # Create quick answer prompt
            prompt = self._create_quick_answer_prompt(analysis_data, question)
            
            # Call Bedrock API with shorter response
            ai_response = self._invoke_model(prompt, max_tokens=500, temperature=0.3)
            
            # Clean and return the response
            cleaned_response = self._clean_response(ai_response)
            
            logger.info("✅ Quick AI answer generated successfully")
            return cleaned_response
            
        except Exception as e:
            logger.error(f"❌ Failed to generate quick answer: {e}")
            return f"Sorry, I couldn't process your question. Error: {str(e)}"
    
    async def generate_anomaly_analysis(self, entries: List[PersonalEntry], anomalies: List[Dict]) -> AIInsight:
        if not self.is_initialized or not self.bedrock_client:
            return self._create_fallback_insight("AWS Bedrock not available")
        
        try:
            # Prepare anomaly data
            analysis_data = self._prepare_analysis_data(entries)
            anomaly_data = {
                "anomalies": anomalies,
                "total_anomalies": len(anomalies),
                "anomaly_types": list(set(a.get("anomaly_type", "unknown") for a in anomalies))
            }
            
            # Create anomaly analysis prompt
            prompt = self._create_anomaly_analysis_prompt(analysis_data, anomaly_data)
            
            # Call Bedrock API
            ai_response = self._invoke_model(prompt, max_tokens=1200, temperature=0.3)
            
            # Extract structured insights
            insight = self._parse_ai_response(ai_response, analysis_data, "anomaly_analysis")
            
            logger.info("✅ Anomaly analysis generated successfully using AWS Bedrock")
            return insight
            
        except Exception as e:
            logger.error(f"❌ Failed to generate anomaly analysis: {e}")
            return self._create_fallback_insight(f"Error: {str(e)}")
    
    
    def _prepare_analysis_data(self, entries: List[PersonalEntry]) -> Dict[str, Any]:
        """Prepare data for AI analysis."""
        if not entries:
            return {"error": "No data available"}
        
        # Basic metrics
        total_entries = len(entries)
        compliant_entries = sum(1 for entry in entries if entry.is_compliant())
        compliance_rate = (compliant_entries / total_entries) * 100
        
        # Equipment analysis
        equipment_stats = defaultdict(lambda: {"total": 0, "violations": 0})
        for entry in entries:
            for equipment, is_present in entry.equipment.items():
                equipment_stats[equipment]["total"] += 1
                if not is_present:
                    equipment_stats[equipment]["violations"] += 1
        
        # Calculate violation rates
        equipment_violations = {}
        for equipment, stats in equipment_stats.items():
            violation_rate = (stats["violations"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            equipment_violations[equipment] = {
                "violations": stats["violations"],
                "total": stats["total"],
                "violation_rate": violation_rate,
                "label": self.equipment_labels.get(equipment, equipment)
            }
        
        # Temporal analysis
        hourly_stats = defaultdict(list)
        daily_stats = defaultdict(list)
        for entry in entries:
            hour = entry.entered_at.hour
            day = entry.entered_at.date()
            hourly_stats[hour].append(entry.is_compliant())
            daily_stats[day].append(entry.is_compliant())
        
        # Calculate hourly compliance rates
        hourly_compliance = {}
        for hour, compliance_list in hourly_stats.items():
            if compliance_list:
                hourly_compliance[hour] = {
                    "compliance_rate": (sum(compliance_list) / len(compliance_list)) * 100,
                    "entries": len(compliance_list)
                }
        
        # Room analysis
        room_stats = defaultdict(lambda: {"entries": 0, "compliant": 0})
        for entry in entries:
            room_stats[entry.room_name]["entries"] += 1
            if entry.is_compliant():
                room_stats[entry.room_name]["compliant"] += 1
        
        # Enhanced room analysis with risk assessment
        room_performance = {}
        room_equipment_issues = defaultdict(lambda: defaultdict(int))
        
        # Track equipment issues by room
        for entry in entries:
            if entry.equipment:
                for equipment, is_present in entry.equipment.items():
                    if not is_present:
                        room_equipment_issues[entry.room_name][equipment] += 1
        
        for room, stats in room_stats.items():
            compliance_rate = (stats["compliant"] / stats["entries"]) * 100 if stats["entries"] > 0 else 0
            violation_count = stats["entries"] - stats["compliant"]
            room_performance[room] = {
                "entries": stats["entries"],
                "compliance_rate": compliance_rate,
                "compliant_entries": stats["compliant"],
                "violations": violation_count,
                "main_equipment_issues": dict(room_equipment_issues[room]),
                "risk_level": "CRITICAL" if compliance_rate < 60 else "HIGH" if compliance_rate < 70 else "MEDIUM" if compliance_rate < 85 else "LOW",
                "needs_attention": compliance_rate < 80
            }
        
        # Time period analysis
        if entries:
            earliest_entry = min(entries, key=lambda x: x.entered_at)
            latest_entry = max(entries, key=lambda x: x.entered_at)
            analysis_period = f"{earliest_entry.entered_at.date()} to {latest_entry.entered_at.date()}"
        else:
            analysis_period = "No data"
        
        # Add shift analysis
        shift_stats = {"morning": [], "afternoon": [], "night": []}
        for entry in entries:
            hour = entry.entered_at.hour
            if 6 <= hour < 14:
                shift_stats["morning"].append(entry.is_compliant())
            elif 14 <= hour < 22:
                shift_stats["afternoon"].append(entry.is_compliant())
            else:
                shift_stats["night"].append(entry.is_compliant())
        
        shift_compliance = {}
        for shift, compliance_list in shift_stats.items():
            if compliance_list:
                shift_compliance[shift] = {
                    "compliance_rate": (sum(compliance_list) / len(compliance_list)) * 100,
                    "entries": len(compliance_list),
                    "violations": len(compliance_list) - sum(compliance_list)
                }
        
        # Critical insights and alerts
        critical_issues = []
        if compliance_rate < 60:
            critical_issues.append("Overall compliance critically low - immediate action required")
        
        worst_equipment = max(equipment_violations.items(), key=lambda x: x[1]["violation_rate"]) if equipment_violations else None
        if worst_equipment and worst_equipment[1]["violation_rate"] > 30:
            critical_issues.append(f"High {worst_equipment[1]['label'].lower()} violation rate requires attention")
        
        worst_room = min(room_performance.items(), key=lambda x: x[1]["compliance_rate"]) if room_performance else None
        if worst_room and worst_room[1]["compliance_rate"] < 70:
            critical_issues.append(f"{worst_room[0]} area has critical compliance issues")
        
        # Business impact metrics
        total_violations = total_entries - compliant_entries
        violation_rate = (total_violations / total_entries * 100) if total_entries > 0 else 0
        
        return {
            "total_entries": total_entries,
            "compliant_entries": compliant_entries,
            "violation_entries": total_violations,
            "compliance_rate": compliance_rate,
            "violation_rate": violation_rate,
            "equipment_violations": equipment_violations,
            "hourly_compliance": hourly_compliance,
            "shift_compliance": shift_compliance,
            "room_performance": room_performance,
            "critical_issues": critical_issues,
            "analysis_period": analysis_period,
            "data_quality": "Excellent" if total_entries > 100 else "Good" if total_entries > 50 else "Fair" if total_entries > 20 else "Limited" if total_entries > 0 else "No data",
            "overall_risk_level": "CRITICAL" if compliance_rate < 60 else "HIGH" if compliance_rate < 70 else "MEDIUM" if compliance_rate < 85 else "LOW",
            "business_impact": {
                "total_safety_violations": total_violations,
                "compliance_score": f"{compliance_rate:.1f}%",
                "needs_immediate_action": compliance_rate < 70,
                "high_risk_rooms": [room for room, stats in room_performance.items() if stats["risk_level"] in ["CRITICAL", "HIGH"]]
            }
        }
    
    def _create_analysis_prompt(self, data: Dict[str, Any], insight_type: str) -> str:
        """Create prompt for AI analysis."""
        prompt = f"""You are an expert safety compliance analyst. Analyze the following safety compliance data and provide professional insights.

DATA OVERVIEW:
- Total Entries: {data['total_entries']}
- Compliance Rate: {data['compliance_rate']:.1f}%
- Analysis Period: {data['analysis_period']}
- Data Quality: {data['data_quality']}

EQUIPMENT VIOLATIONS:
"""
        
        for equipment, stats in data['equipment_violations'].items():
            prompt += f"- {stats['label']}: {stats['violation_rate']:.1f}% violation rate ({stats['violations']}/{stats['total']} entries)\n"
        
        prompt += f"""
HOURLY COMPLIANCE PATTERNS:
"""
        
        # Add top 3 worst hours
        worst_hours = sorted(data['hourly_compliance'].items(), key=lambda x: x[1]['compliance_rate'])[:3]
        for hour, stats in worst_hours:
            prompt += f"- {hour}:00 - {stats['compliance_rate']:.1f}% compliance ({stats['entries']} entries)\n"
        
        prompt += f"""
ROOM PERFORMANCE:
"""
        
        for room, stats in data['room_performance'].items():
            prompt += f"- {room}: {stats['compliance_rate']:.1f}% compliance ({stats['entries']} entries)\n"
        
        prompt += f"""

Please provide a {insight_type} analysis including:
1. Executive Summary (2-3 sentences)
2. Key Findings (3-5 bullet points)
3. Risk Assessment (Low/Medium/High with reasoning)
4. Actionable Recommendations (3-5 specific actions)
5. Confidence Level (0-100%)

Format your response as structured JSON with these fields:
- summary
- key_findings (array)
- risk_level
- recommendations (array)
- confidence_score

IMPORTANT: Return ONLY valid JSON without any markdown formatting, code blocks, or additional text. Do not wrap the response in ```json``` or any other formatting.
"""
        
        return prompt
    
    def _create_executive_report_prompt(self, data: Dict[str, Any]) -> str:
        """Create prompt for executive report."""
        prompt = f"""Generate a comprehensive executive safety compliance report based on this data:

COMPLIANCE METRICS:
- Total Entries: {data['total_entries']}
- Overall Compliance Rate: {data['compliance_rate']:.1f}%
- Analysis Period: {data['analysis_period']}

EQUIPMENT PERFORMANCE:
"""
        
        for equipment, stats in data['equipment_violations'].items():
            prompt += f"- {stats['label']}: {stats['violation_rate']:.1f}% violations\n"
        
        prompt += f"""
OPERATIONAL INSIGHTS:
- Peak violation hours: {', '.join([f"{h}:00" for h, s in sorted(data['hourly_compliance'].items(), key=lambda x: x[1]['compliance_rate'])[:3]])}
- Room performance varies from {min(data['room_performance'].values(), key=lambda x: x['compliance_rate'])['compliance_rate']:.1f}% to {max(data['room_performance'].values(), key=lambda x: x['compliance_rate'])['compliance_rate']:.1f}%

Please provide:
1. Executive Summary (3-4 sentences)
2. Compliance Overview (key metrics and trends)
3. Trend Analysis (performance patterns)
4. Risk Assessment (overall risk level and factors)
5. Strategic Action Items (prioritized recommendations)

Format as structured JSON with fields:
- executive_summary
- compliance_overview
- trend_analysis
- risk_assessment
- action_items (array of objects with title, priority, deadline)

IMPORTANT: Return ONLY valid JSON without any markdown formatting, code blocks, or additional text. Do not wrap the response in ```json``` or any other formatting.
"""
        
        return prompt
    
    def _create_anomaly_analysis_prompt(self, data: Dict[str, Any], anomaly_data: Dict) -> str:
        """Create prompt for anomaly analysis."""
        prompt = f"""Analyze these detected anomalies in safety compliance data:

ANOMALY SUMMARY:
- Total Anomalies Detected: {anomaly_data['total_anomalies']}
- Anomaly Types: {', '.join(anomaly_data['anomaly_types'])}

CURRENT COMPLIANCE CONTEXT:
- Overall Compliance Rate: {data['compliance_rate']:.1f}%
- Total Entries Analyzed: {data['total_entries']}

DETAILED ANOMALIES:
"""
        
        for i, anomaly in enumerate(anomaly_data['anomalies'][:5]):  # Limit to top 5
            prompt += f"{i+1}. {anomaly.get('description', 'Unknown anomaly')} (Severity: {anomaly.get('severity', 'unknown')})\n"
        
        prompt += """

Provide analysis including:
1. Root Cause Analysis (why these anomalies occurred)
2. Impact Assessment (business/safety implications)
3. Mitigation Strategies (how to prevent recurrence)
4. Immediate Actions Required (urgent steps)
5. Long-term Recommendations (systemic improvements)

Format as structured JSON with fields:
- summary
- key_findings (array)
- risk_level
- recommendations (array)
- confidence_score

IMPORTANT: Return ONLY valid JSON without any markdown formatting, code blocks, or additional text. Do not wrap the response in ```json``` or any other formatting.
"""
        
        return prompt
    
    def _create_custom_analysis_prompt(self, data: Dict[str, Any], user_prompt: str) -> str:
        """Create enhanced prompt for detailed factory safety analysis."""
        # Classify the question for targeted analysis
        question_type = self._classify_question(user_prompt)
        
        prompt = f"""You are a senior factory safety compliance analyst specializing in Personal Protective Equipment (PPE) monitoring and workplace safety management.

ANALYSIS TYPE: {question_type.upper()} ANALYSIS
USER'S QUESTION: "{user_prompt}"

FACTORY SAFETY OVERVIEW:
- Total Factory Entries Analyzed: {data['total_entries']}
- Overall Safety Compliance Rate: {data['compliance_rate']:.1f}%
- Analysis Period: {data['analysis_period']}
- Data Quality Assessment: {data['data_quality']}
- Current Risk Level: {'CRITICAL' if data['compliance_rate'] < 60 else 'HIGH' if data['compliance_rate'] < 70 else 'MEDIUM' if data['compliance_rate'] < 90 else 'LOW'}

DETAILED PPE COMPLIANCE BREAKDOWN:
"""
        
        # Enhanced equipment analysis with context
        for equipment, stats in data['equipment_violations'].items():
            risk_indicator = "⚠️ HIGH RISK" if stats['violation_rate'] > 20 else "⚡ MODERATE RISK" if stats['violation_rate'] > 10 else "✓ LOW RISK"
            prompt += f"- {stats['label']}: {stats['violation_rate']:.1f}% violations ({stats['violations']}/{stats['total']} entries) - {risk_indicator}\n"
        
        prompt += f"""
FACILITY AREA PERFORMANCE ANALYSIS:
"""
        # Sort rooms by compliance rate for better insights
        sorted_rooms = sorted(data['room_performance'].items(), key=lambda x: x[1]['compliance_rate'])
        for room, stats in sorted_rooms:
            performance_level = stats.get('risk_level', 'UNKNOWN')
            prompt += f"- {room}: {stats['compliance_rate']:.1f}% compliant ({stats['entries']} entries) - {performance_level} RISK\n"
            if 'main_equipment_issues' in stats and stats['main_equipment_issues']:
                main_issues = sorted(stats['main_equipment_issues'].items(), key=lambda x: x[1], reverse=True)[:2]
                issue_text = ", ".join([f"{eq}({count})" for eq, count in main_issues])
                prompt += f"  Primary violations: {issue_text}\n"
        
        prompt += f"""
TEMPORAL COMPLIANCE PATTERNS:
"""
        
        # Enhanced shift and hourly analysis
        if 'shift_compliance' in data and data['shift_compliance']:
            prompt += "Shift Performance Analysis:\n"
            for shift, stats in data['shift_compliance'].items():
                shift_risk = "HIGH RISK" if stats['compliance_rate'] < 70 else "MEDIUM RISK" if stats['compliance_rate'] < 85 else "LOW RISK"
                prompt += f"- {shift.title()} shift: {stats['compliance_rate']:.1f}% compliant ({stats['entries']} entries, {stats.get('violations', 0)} violations) - {shift_risk}\n"
        
        if 'hourly_compliance' in data and data['hourly_compliance']:
            worst_hours = sorted(data['hourly_compliance'].items(), key=lambda x: x[1]['compliance_rate'])[:3]
            best_hours = sorted(data['hourly_compliance'].items(), key=lambda x: x[1]['compliance_rate'], reverse=True)[:2]
            
            prompt += "Worst Performance Hours:\n"
            for hour, stats in worst_hours:
                prompt += f"- {hour}:00 - {stats['compliance_rate']:.1f}% compliant ({stats['entries']} entries)\n"
            
            prompt += "Best Performance Hours:\n"
            for hour, stats in best_hours:
                prompt += f"- {hour}:00 - {stats['compliance_rate']:.1f}% compliant ({stats['entries']} entries)\n"
        
        # Add critical issues and business impact
        if 'critical_issues' in data and data['critical_issues']:
            prompt += f"""
CRITICAL SAFETY ALERTS:
"""
            for issue in data['critical_issues']:
                prompt += f"- {issue}\n"
        
        if 'business_impact' in data:
            business = data['business_impact']
            prompt += f"""
BUSINESS IMPACT ASSESSMENT:
- Total Safety Violations: {business.get('total_safety_violations', 'N/A')}
- Compliance Score: {business.get('compliance_score', 'N/A')}
- Immediate Action Required: {'YES' if business.get('needs_immediate_action', False) else 'NO'}
- High Risk Areas: {', '.join(business.get('high_risk_rooms', [])) if business.get('high_risk_rooms') else 'None'}
"""
        
        # Add specific analysis guidance based on question type
        prompt += f"""

ANALYSIS FOCUS FOR {question_type.upper()}:
"""
        
        if question_type == "compliance_overview":
            prompt += """- Provide comprehensive compliance status assessment
- Identify main safety compliance challenges
- Compare current performance against safety standards
- Assess overall factory safety health"""
        elif question_type == "equipment_specific":
            prompt += """- Deep dive into specific PPE compliance issues
- Identify equipment-specific violation patterns
- Analyze impact of missing equipment on safety
- Provide equipment-specific improvement strategies"""
        elif question_type == "room_performance":
            prompt += """- Compare performance across different factory areas
- Identify high-risk zones requiring immediate attention
- Analyze room-specific safety challenges
- Recommend area-specific safety interventions"""
        elif question_type == "risk_assessment":
            prompt += """- Conduct comprehensive safety risk evaluation
- Identify immediate and long-term safety threats
- Prioritize safety issues by severity and impact
- Provide emergency response recommendations"""
        elif question_type == "time_patterns":
            prompt += """- Analyze temporal trends in safety compliance
- Identify time-based risk patterns
- Evaluate shift performance and scheduling impacts
- Recommend time-based safety interventions"""
        elif question_type == "recommendations":
            prompt += """- Develop actionable safety improvement strategies
- Prioritize recommendations by impact and feasibility
- Provide implementation timelines and resource requirements
- Create measurable safety improvement goals"""
        
        prompt += f"""

COMPREHENSIVE ANALYSIS REQUIREMENTS:
1. Direct, data-driven answer to: "{user_prompt}"
2. Supporting evidence from compliance data with specific numbers
3. Key insights relevant to factory safety and operational efficiency
4. Actionable safety recommendations with implementation priorities
5. Risk assessment with urgency levels and potential safety impacts
6. ROI considerations for safety improvements where applicable

Format your response as structured JSON with these fields:
- summary: Comprehensive answer directly addressing the user's question (2-3 sentences)
- key_findings: Array of 4-6 critical insights with data support
- risk_level: "low", "medium", "high", or "critical" with justification
- recommendations: Array of 4-6 specific, actionable safety improvements
- confidence_score: 0-100% based on data quality and analysis certainty

Use professional factory safety terminology. Focus on:
- PPE compliance and safety protocols
- Operational safety risks and mitigation strategies  
- Regulatory compliance and safety standards
- Cost-benefit analysis of safety improvements
- Employee safety and training needs

IMPORTANT: Return ONLY valid JSON without any markdown formatting, code blocks, or additional text. Do not wrap the response in ```json``` or any other formatting.
"""
        
        return prompt
    
    def _create_quick_answer_prompt(self, data: Dict[str, Any], question: str) -> str:
        """Create enhanced prompt for quick answer with factory safety context."""
        # Classify the question type for targeted responses
        question_type = self._classify_question(question)
        
        prompt = f"""You are a factory safety compliance expert specializing in Personal Protective Equipment (PPE) monitoring. 

QUESTION TYPE: {question_type}
USER'S QUESTION: "{question}"

CURRENT SAFETY STATUS:
- Total Factory Entries: {data['total_entries']}
- Overall Compliance Rate: {data['compliance_rate']:.1f}%
- Analysis Period: {data['analysis_period']}
- Risk Level: {'HIGH' if data['compliance_rate'] < 70 else 'MEDIUM' if data['compliance_rate'] < 90 else 'LOW'}

EQUIPMENT VIOLATIONS (PPE MISSING):
"""
        
        for equipment, stats in data['equipment_violations'].items():
            if stats['violation_rate'] > 0:
                prompt += f"- {stats['label']}: {stats['violation_rate']:.1f}% violations ({stats['violations']}/{stats['total']} entries)\n"
        
        # Add room-specific data with risk levels
        if 'room_performance' in data and data['room_performance']:
            prompt += f"\nROOM SAFETY PERFORMANCE:\n"
            for room, stats in sorted(data['room_performance'].items(), key=lambda x: x[1]['compliance_rate']):
                risk_indicator = f" ({stats.get('risk_level', 'UNKNOWN')} RISK)" if 'risk_level' in stats else ""
                prompt += f"- {room}: {stats['compliance_rate']:.1f}% compliant ({stats['entries']} entries){risk_indicator}\n"
                if 'main_equipment_issues' in stats and stats['main_equipment_issues']:
                    top_issue = max(stats['main_equipment_issues'].items(), key=lambda x: x[1])
                    prompt += f"  Main issue: {top_issue[0]} ({top_issue[1]} violations)\n"
        
        # Add shift performance if available
        if 'shift_compliance' in data and data['shift_compliance']:
            prompt += f"\nSHIFT PERFORMANCE:\n"
            for shift, stats in data['shift_compliance'].items():
                prompt += f"- {shift.title()} shift: {stats['compliance_rate']:.1f}% compliant ({stats['entries']} entries, {stats.get('violations', 0)} violations)\n"
        
        # Add critical issues
        if 'critical_issues' in data and data['critical_issues']:
            prompt += f"\nCRITICAL SAFETY ALERTS:\n"
            for issue in data['critical_issues']:
                prompt += f"- {issue}\n"
        
        # Add time-based patterns if available
        if 'hourly_compliance' in data and data['hourly_compliance']:
            worst_hours = sorted(data['hourly_compliance'].items(), key=lambda x: x[1]['compliance_rate'])[:3]
            if worst_hours:
                prompt += f"\nWORST COMPLIANCE HOURS:\n"
                for hour, stats in worst_hours:
                    prompt += f"- {hour}:00 - {stats['compliance_rate']:.1f}% compliant ({stats['entries']} entries)\n"
        
        prompt += f"""

RESPONSE GUIDELINES FOR {question_type.upper()}:
"""
        
        # Add specific guidance based on question type
        if question_type == "compliance_overview":
            prompt += "Focus on overall compliance rates, main violations, and safety status summary."
        elif question_type == "equipment_specific":
            prompt += "Focus on specific equipment violations, trends, and recommendations for that equipment type."
        elif question_type == "room_performance":
            prompt += "Focus on room-specific compliance data, comparisons between rooms, and room-specific issues."
        elif question_type == "risk_assessment":
            prompt += "Focus on safety risks, urgency levels, and immediate actions needed."
        elif question_type == "time_patterns":
            prompt += "Focus on time-based patterns, shift performance, and temporal trends in compliance."
        elif question_type == "recommendations":
            prompt += "Focus on actionable recommendations, improvement strategies, and next steps."
        else:
            prompt += "Provide a comprehensive answer addressing the specific safety compliance question."
        
        prompt += f"""

Provide a concise, direct answer using actual data numbers. Be specific about:
- Current safety status and compliance rates
- Specific violations and their impact
- Immediate safety concerns if any
- Clear, actionable insights

Keep response under 200 words. Use factory safety terminology (PPE, compliance, violations, safety protocols).
Do not use markdown formatting or code blocks. Provide a clear, professional safety analysis.
"""
        
        return prompt
    
    def _classify_question(self, question: str) -> str:
        """Classify the type of safety compliance question for targeted responses."""
        question_lower = question.lower()
        
        # Equipment-specific questions
        if any(equipment in question_lower for equipment in ['mask', 'glove', 'hairnet', 'glasses', 'equipment']):
            return "equipment_specific"
        
        # Room/location-specific questions  
        if any(room in question_lower for room in ['room', 'floor', 'area', 'line', 'production', 'assembly', 'packaging']):
            return "room_performance"
        
        # Risk and safety assessment questions
        if any(risk_word in question_lower for risk_word in ['risk', 'danger', 'safety', 'critical', 'urgent', 'problem']):
            return "risk_assessment"
        
        # Time-based questions
        if any(time_word in question_lower for time_word in ['hour', 'shift', 'time', 'when', 'trend', 'pattern']):
            return "time_patterns"
        
        # Recommendation questions
        if any(rec_word in question_lower for rec_word in ['improve', 'fix', 'solve', 'recommend', 'should', 'how']):
            return "recommendations"
        
        # Overall compliance questions
        if any(comp_word in question_lower for comp_word in ['compliance', 'overall', 'rate', 'performance', 'status']):
            return "compliance_overview"
        
        return "general"
    
    def _parse_custom_response(self, response: str, data: Dict[str, Any], user_prompt: str) -> AIInsight:
        """Parse custom AI response into structured insight."""
        try:
            # Clean the response - remove markdown code blocks
            cleaned_response = self._clean_response(response)
            
            # Try to extract JSON from response
            json_start = cleaned_response.find('{')
            json_end = cleaned_response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = cleaned_response[json_start:json_end]
                parsed = json.loads(json_str)
                
                return AIInsight(
                    insight_type="custom_analysis",
                    title=f"Custom Analysis: {user_prompt[:50]}...",
                    summary=parsed.get('summary', 'Analysis completed'),
                    detailed_analysis=cleaned_response,
                    key_findings=parsed.get('key_findings', []),
                    recommendations=parsed.get('recommendations', []),
                    risk_level=parsed.get('risk_level', 'medium'),
                    confidence_score=parsed.get('confidence_score', 75),
                    generated_at=datetime.now(),
                    data_period=data.get('analysis_period', 'Unknown'),
                    model_used=self.model_id
                )
            else:
                # Fallback if no JSON found
                return AIInsight(
                    insight_type="custom_analysis",
                    title=f"Custom Analysis: {user_prompt[:50]}...",
                    summary="Analysis completed",
                    detailed_analysis=cleaned_response,
                    key_findings=["Analysis completed successfully"],
                    recommendations=["Review detailed analysis for specific recommendations"],
                    risk_level="medium",
                    confidence_score=70,
                    generated_at=datetime.now(),
                    data_period=data.get('analysis_period', 'Unknown'),
                    model_used=self.model_id
                )
                
        except Exception as e:
            logger.error(f"Failed to parse custom AI response: {e}")
            return self._create_fallback_insight(f"Parsing error: {str(e)}")
    
    def _clean_response(self, response: str) -> str:
        """Clean AI response by removing markdown formatting."""
        cleaned_response = response.strip()
        
        # Remove ```json and ``` markers if present
        if cleaned_response.startswith('```json'):
            cleaned_response = cleaned_response[7:]  # Remove ```json
        elif cleaned_response.startswith('```'):
            cleaned_response = cleaned_response[3:]  # Remove ```
        
        if cleaned_response.endswith('```'):
            cleaned_response = cleaned_response[:-3]  # Remove trailing ```
        
        return cleaned_response.strip()
    
    def _parse_ai_response(self, response: str, data: Dict[str, Any], insight_type: str) -> AIInsight:
        """Parse AI response into structured insight."""
        try:
            # Clean the response - remove markdown code blocks
            cleaned_response = response.strip()
            
            # Remove ```json and ``` markers if present
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]  # Remove ```
            
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove trailing ```
            
            cleaned_response = cleaned_response.strip()
            
            # Try to extract JSON from response
            json_start = cleaned_response.find('{')
            json_end = cleaned_response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = cleaned_response[json_start:json_end]
                parsed = json.loads(json_str)
                
                return AIInsight(
                    insight_type=insight_type,
                    title=f"AI Analysis - {insight_type.title()}",
                    summary=parsed.get('summary', 'Analysis completed'),
                    detailed_analysis=parsed.get('detailed_analysis', cleaned_response),
                    key_findings=parsed.get('key_findings', []),
                    recommendations=parsed.get('recommendations', []),
                    risk_level=parsed.get('risk_level', 'medium'),
                    confidence_score=parsed.get('confidence_score', 75),
                    generated_at=datetime.now(),
                    data_period=data.get('analysis_period', 'Unknown'),
                    model_used=self.model_id
                )
            else:
                # Fallback if no JSON found
                return AIInsight(
                    insight_type=insight_type,
                    title=f"AI Analysis - {insight_type.title()}",
                    summary="Analysis completed",
                    detailed_analysis=cleaned_response,
                    key_findings=["Analysis completed successfully"],
                    recommendations=["Review detailed analysis for specific recommendations"],
                    risk_level="medium",
                    confidence_score=70,
                    generated_at=datetime.now(),
                    data_period=data.get('analysis_period', 'Unknown'),
                    model_used=self.model_id
                )
                
        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            return self._create_fallback_insight(f"Parsing error: {str(e)}")
    
    def _parse_executive_report(self, response: str, data: Dict[str, Any]) -> ComplianceReport:
        """Parse AI response into executive report."""
        try:
            # Clean the response - remove markdown code blocks
            cleaned_response = response.strip()
            
            # Remove ```json and ``` markers if present
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response[7:]  # Remove ```json
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response[3:]  # Remove ```
            
            if cleaned_response.endswith('```'):
                cleaned_response = cleaned_response[:-3]  # Remove trailing ```
            
            cleaned_response = cleaned_response.strip()
            
            # Try to extract JSON from response
            json_start = cleaned_response.find('{')
            json_end = cleaned_response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = cleaned_response[json_start:json_end]
                parsed = json.loads(json_str)
                
                return ComplianceReport(
                    executive_summary=parsed.get('executive_summary', 'Report generated'),
                    compliance_overview=parsed.get('compliance_overview', data),
                    trend_analysis=parsed.get('trend_analysis', 'Trend analysis completed'),
                    risk_assessment=parsed.get('risk_assessment', 'Risk assessment completed'),
                    action_items=parsed.get('action_items', []),
                    insights=[],  # Could be populated with additional insights
                    generated_at=datetime.now(),
                    model_used=self.model_id
                )
            else:
                # Fallback if no JSON found
                return ComplianceReport(
                    executive_summary="Executive report generated",
                    compliance_overview=data,
                    trend_analysis="Trend analysis completed",
                    risk_assessment="Risk assessment completed",
                    action_items=[],
                    insights=[],
                    generated_at=datetime.now(),
                    model_used=self.model_id
                )
                
        except Exception as e:
            logger.error(f"Failed to parse executive report: {e}")
            return self._create_fallback_report(f"Parsing error: {str(e)}")
    
    def _create_fallback_insight(self, reason: str) -> AIInsight:
        """Create fallback insight when AI is not available."""
        return AIInsight(
            insight_type="fallback",
            title="Analysis Unavailable",
            summary=f"AI analysis not available: {reason}",
            detailed_analysis=f"AWS Bedrock service is not available or configured. Reason: {reason}",
            key_findings=["Manual analysis required"],
            recommendations=["Configure AWS Bedrock for AI-powered insights"],
            risk_level="unknown",
            confidence_score=0,
            generated_at=datetime.now(),
            data_period="Unknown",
            model_used="none"
        )
    
    def _create_fallback_report(self, reason: str) -> ComplianceReport:
        """Create fallback report when AI is not available."""
        return ComplianceReport(
            executive_summary=f"AI report generation unavailable: {reason}",
            compliance_overview={"error": reason},
            trend_analysis="Manual analysis required",
            risk_assessment="Risk assessment unavailable",
            action_items=[],
            insights=[],
            generated_at=datetime.now(),
            model_used="none"
        )

# Global instance
bedrock_nlp = BedrockNLPanalytics()
