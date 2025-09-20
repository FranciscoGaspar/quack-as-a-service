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
    
    async def generate_anomaly_analysis(self, entries: List[PersonalEntry], anomalies: List[Dict]) -> AIInsight:
        """Generate AI analysis of detected anomalies using AWS Bedrock."""
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
        
        room_performance = {}
        for room, stats in room_stats.items():
            compliance_rate = (stats["compliant"] / stats["entries"]) * 100 if stats["entries"] > 0 else 0
            room_performance[room] = {
                "entries": stats["entries"],
                "compliance_rate": compliance_rate
            }
        
        # Time period analysis
        if entries:
            earliest_entry = min(entries, key=lambda x: x.entered_at)
            latest_entry = max(entries, key=lambda x: x.entered_at)
            analysis_period = f"{earliest_entry.entered_at.date()} to {latest_entry.entered_at.date()}"
        else:
            analysis_period = "No data"
        
        return {
            "total_entries": total_entries,
            "compliant_entries": compliant_entries,
            "compliance_rate": compliance_rate,
            "equipment_violations": equipment_violations,
            "hourly_compliance": hourly_compliance,
            "room_performance": room_performance,
            "analysis_period": analysis_period,
            "data_quality": "good" if total_entries >= 20 else "limited"
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
