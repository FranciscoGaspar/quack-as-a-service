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
    
    async def generate_emotional_analysis(self, entries: List[PersonalEntry]) -> AIInsight:
        """Generate AI-powered emotional analysis using AWS Bedrock."""
        if not self.is_initialized or not self.bedrock_client:
            return self._create_fallback_insight("AWS Bedrock not available")
        
        try:
            # Prepare emotional analysis data
            emotional_data = self._prepare_emotional_analysis_data(entries)
            
            # Create emotional analysis prompt
            prompt = self._create_emotional_analysis_prompt(emotional_data)
            
            # Call Bedrock API
            ai_response = self._invoke_model(prompt, max_tokens=1500, temperature=0.3)
            
            # Extract structured insights
            insight = self._parse_ai_response(ai_response, emotional_data, "emotional_analysis")
            
            logger.info("✅ Emotional analysis generated successfully using AWS Bedrock")
            return insight
            
        except Exception as e:
            logger.error(f"❌ Failed to generate emotional analysis: {e}")
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
    
    def _prepare_emotional_analysis_data(self, entries: List[PersonalEntry]) -> Dict[str, Any]:
        """Prepare emotional analysis data for AI analysis."""
        if not entries:
            return {"error": "No data available"}
        
        # Filter entries with emotional analysis
        entries_with_emotions = [entry for entry in entries if entry.emotional_analysis]
        
        if not entries_with_emotions:
            return {
                "error": "No emotional analysis data available",
                "total_entries": len(entries),
                "entries_with_emotions": 0
            }
        
        # Basic metrics
        total_entries = len(entries)
        entries_with_emotions_count = len(entries_with_emotions)
        emotional_coverage = (entries_with_emotions_count / total_entries) * 100
        
        # Emotion distribution analysis
        emotion_counts = {}
        confidence_scores = []
        image_quality_counts = {}
        faces_detected_counts = []
        
        # Room-based emotional patterns
        room_emotions = defaultdict(list)
        
        # Time-based emotional patterns
        hourly_emotions = defaultdict(list)
        daily_emotions = defaultdict(list)
        
        for entry in entries_with_emotions:
            analysis = entry.emotional_analysis
            
            # Count emotions
            if analysis.dominant_emotion:
                emotion_counts[analysis.dominant_emotion] = emotion_counts.get(analysis.dominant_emotion, 0) + 1
                room_emotions[entry.room_name].append(analysis.dominant_emotion)
            
            # Collect confidence scores
            if analysis.overall_confidence:
                confidence_scores.append(analysis.overall_confidence)
            
            # Count image quality
            if analysis.image_quality:
                image_quality_counts[analysis.image_quality] = image_quality_counts.get(analysis.image_quality, 0) + 1
            
            # Collect faces detected
            faces_detected_counts.append(analysis.faces_detected)
            
            # Time-based analysis
            hour = entry.entered_at.hour
            day = entry.entered_at.date()
            if analysis.dominant_emotion:
                hourly_emotions[hour].append(analysis.dominant_emotion)
                daily_emotions[day].append(analysis.dominant_emotion)
        
        # Calculate emotion percentages
        emotion_percentages = {}
        for emotion, count in emotion_counts.items():
            emotion_percentages[emotion] = (count / entries_with_emotions_count) * 100
        
        # Calculate average confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Calculate image quality distribution
        image_quality_percentages = {}
        for quality, count in image_quality_counts.items():
            image_quality_percentages[quality] = (count / entries_with_emotions_count) * 100
        
        # Calculate average faces detected
        avg_faces_detected = sum(faces_detected_counts) / len(faces_detected_counts) if faces_detected_counts else 0
        
        # Room emotional patterns
        room_emotional_patterns = {}
        for room, emotions in room_emotions.items():
            if emotions:
                emotion_counter = Counter(emotions)
                most_common_emotion = emotion_counter.most_common(1)[0]
                room_emotional_patterns[room] = {
                    "most_common_emotion": most_common_emotion[0],
                    "emotion_frequency": most_common_emotion[1],
                    "total_emotional_entries": len(emotions),
                    "emotion_distribution": dict(emotion_counter)
                }
        
        # Time period analysis
        if entries_with_emotions:
            earliest_entry = min(entries_with_emotions, key=lambda x: x.entered_at)
            latest_entry = max(entries_with_emotions, key=lambda x: x.entered_at)
            analysis_period = f"{earliest_entry.entered_at.date()} to {latest_entry.entered_at.date()}"
        else:
            analysis_period = "No data"
        
        # Find most common emotion overall
        most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1]) if emotion_counts else None
        
        return {
            "total_entries": total_entries,
            "entries_with_emotions": entries_with_emotions_count,
            "emotional_coverage": emotional_coverage,
            "emotion_distribution": emotion_percentages,
            "most_common_emotion": most_common_emotion[0] if most_common_emotion else None,
            "most_common_emotion_count": most_common_emotion[1] if most_common_emotion else 0,
            "average_confidence": avg_confidence,
            "image_quality_distribution": image_quality_percentages,
            "average_faces_detected": avg_faces_detected,
            "room_emotional_patterns": room_emotional_patterns,
            "analysis_period": analysis_period,
            "data_quality": "good" if entries_with_emotions_count >= 10 else "limited"
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
    
    def _create_emotional_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Create prompt for emotional analysis."""
        if data.get("error"):
            return f"""You are an expert workplace psychology and emotional intelligence analyst. 

ERROR: {data['error']}

Please provide a brief analysis explaining why emotional analysis data is not available and what steps should be taken to collect this valuable workplace wellness data.

Format as structured JSON with fields:
- summary
- key_findings (array)
- risk_level
- recommendations (array)
- confidence_score

IMPORTANT: Return ONLY valid JSON without any markdown formatting, code blocks, or additional text. Do not wrap the response in ```json``` or any other formatting.
"""
        
        prompt = f"""You are an expert workplace psychology and emotional intelligence analyst. Analyze the following emotional data from workplace entries and provide comprehensive insights about employee emotional well-being and workplace culture.

EMOTIONAL DATA OVERVIEW:
- Total Entries: {data['total_entries']}
- Entries with Emotional Analysis: {data['entries_with_emotions']}
- Emotional Data Coverage: {data['emotional_coverage']:.1f}%
- Analysis Period: {data['analysis_period']}
- Data Quality: {data['data_quality']}

EMOTION DISTRIBUTION:
"""
        
        for emotion, percentage in data['emotion_distribution'].items():
            prompt += f"- {emotion}: {percentage:.1f}% of emotional entries\n"
        
        prompt += f"""
MOST COMMON EMOTION: {data['most_common_emotion']} ({data['most_common_emotion_count']} occurrences)
AVERAGE CONFIDENCE LEVEL: {data['average_confidence']:.1f}%
AVERAGE FACES DETECTED: {data['average_faces_detected']:.1f}

IMAGE QUALITY DISTRIBUTION:
"""
        
        for quality, percentage in data['image_quality_distribution'].items():
            prompt += f"- {quality}: {percentage:.1f}%\n"
        
        prompt += f"""
ROOM EMOTIONAL PATTERNS:
"""
        
        for room, patterns in data['room_emotional_patterns'].items():
            prompt += f"- {room}: Most common emotion is {patterns['most_common_emotion']} ({patterns['emotion_frequency']}/{patterns['total_emotional_entries']} entries)\n"
        
        prompt += f"""

Please provide a comprehensive emotional analysis including:

1. EXECUTIVE SUMMARY (2-3 sentences about overall emotional climate)
2. KEY FINDINGS (4-6 bullet points about emotional patterns, workplace culture, and employee well-being)
3. RISK ASSESSMENT (Low/Medium/High with specific reasoning about emotional health risks)
4. ACTIONABLE RECOMMENDATIONS (4-6 specific actions to improve emotional well-being and workplace culture)
5. CONFIDENCE LEVEL (0-100% based on data quality and sample size)

Focus on:
- Employee emotional well-being and mental health indicators
- Workplace culture and environment assessment
- Potential stress factors and their impact
- Recommendations for improving emotional climate
- Risk factors for employee burnout or dissatisfaction
- Positive emotional patterns to reinforce

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
        """Create prompt for custom user analysis."""
        prompt = f"""You are an expert safety compliance analyst. A user has asked a specific question about their compliance data.

USER'S QUESTION: "{user_prompt}"

COMPLIANCE DATA CONTEXT:
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

Please answer the user's question: "{user_prompt}"

Provide a comprehensive analysis that directly addresses their question, including:
1. Direct answer to their question
2. Supporting data and evidence
3. Key insights relevant to their question
4. Actionable recommendations if applicable
5. Risk assessment if relevant

Format your response as structured JSON with these fields:
- summary (direct answer to their question)
- key_findings (array of relevant insights)
- risk_level (if applicable)
- recommendations (array of actionable items)
- confidence_score (0-100%)

IMPORTANT: Return ONLY valid JSON without any markdown formatting, code blocks, or additional text. Do not wrap the response in ```json``` or any other formatting.
"""
        
        return prompt
    
    def _create_quick_answer_prompt(self, data: Dict[str, Any], question: str) -> str:
        """Create prompt for quick answer."""
        prompt = f"""You are a safety compliance expert. Answer this question concisely based on the compliance data:

QUESTION: "{question}"

DATA SUMMARY:
- Total Entries: {data['total_entries']}
- Compliance Rate: {data['compliance_rate']:.1f}%
- Analysis Period: {data['analysis_period']}

EQUIPMENT ISSUES:
"""
        
        for equipment, stats in data['equipment_violations'].items():
            if stats['violation_rate'] > 0:
                prompt += f"- {stats['label']}: {stats['violation_rate']:.1f}% violations\n"
        
        prompt += f"""

Provide a concise, direct answer to the user's question. Be specific and use the actual data numbers. 
Keep your response under 200 words and focus on the most important points.

Do not use markdown formatting or code blocks. Just provide a clear, direct answer.
"""
        
        return prompt
    
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
