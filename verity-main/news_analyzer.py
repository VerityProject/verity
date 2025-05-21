from textblob import TextBlob
import re
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Lists of emotionally charged words
EMOTIONAL_WORDS = {
    'positive': [
        'amazing', 'awesome', 'breakthrough', 'brilliant', 'celebrate', 'delight', 
        'excellent', 'extraordinary', 'fantastic', 'remarkable', 'triumph', 'wonderful',
        'victory', 'success', 'happy', 'joyful', 'praise', 'champion', 'perfect'
    ],
    'negative': [
        'awful', 'catastrophe', 'crisis', 'devastating', 'disaster', 'horrible', 
        'terrible', 'tragic', 'alarming', 'destroy', 'danger', 'deadly', 'fail', 
        'threat', 'worst', 'panic', 'fear', 'chaos', 'fury', 'outrage', 'slam'
    ],
    'controversial': [
        'controversy', 'controversial', 'allegedly', 'shocking', 'scandal', 
        'outrageous', 'debate', 'clash', 'conflict', 'dispute', 'accused', 
        'polarizing', 'disputed', 'contentious', 'divided'
    ]
}

# Add war-specific emotional words
WAR_EMOTIONAL_WORDS = {
    'positive': [
        'liberate', 'defend', 'protect', 'secure', 'alliance', 'stability', 
        'peace', 'victory', 'breakthrough', 'reclaim', 'courage', 'heroic'
    ],
    'negative': [
        'invasion', 'attack', 'casualties', 'bombing', 'violence', 'atrocities', 
        'war crime', 'missile', 'strike', 'offensive', 'invasion', 'occupation',
        'regime', 'escalation', 'ultimatum', 'threat'
    ],
    'controversial': [
        'operation', 'incursion', 'conflict', 'tension', 'confrontation', 'dispute',
        'insurgent', 'militant', 'rebel', 'resistance', 'separatist', 'loyalist'
    ]
}

# Add war-specific words to the main emotional words dictionary
for category in WAR_EMOTIONAL_WORDS:
    EMOTIONAL_WORDS[category].extend(WAR_EMOTIONAL_WORDS[category])

def analyze_headline(headline):
    """
    Analyze a news headline for emotional bias
    
    Args:
        headline (str): The news headline to analyze
        
    Returns:
        dict: Analysis results including bias score and category
    """
    try:
        # Perform sentiment analysis with TextBlob
        headline_text = headline.lower()
        analysis = TextBlob(headline_text)
        
        # Get polarity score (-1 to 1 where -1 is very negative, 1 is very positive)
        polarity = analysis.sentiment.polarity
        
        # Get subjectivity score (0 to 1 where 0 is objective, 1 is subjective)
        subjectivity = analysis.sentiment.subjectivity
        
        # Count emotional words
        emotional_word_count = 0
        found_words = []
        
        # Check for emotional words
        for category, words in EMOTIONAL_WORDS.items():
            for word in words:
                pattern = r'\b' + re.escape(word) + r'\b'
                if re.search(pattern, headline_text):
                    emotional_word_count += 1
                    found_words.append(word)
        
        # Calculate combined bias score (blend of polarity, subjectivity, and emotional words)
        # Scale polarity to 0-1 range for easier combination
        polarity_abs = abs(polarity)
        
        # Normalize emotional word count (cap at 3 for scaling)
        emotional_factor = min(emotional_word_count, 3) / 3
        
        # Combined bias score (weighted average of factors)
        bias_score = (0.3 * polarity_abs) + (0.4 * subjectivity) + (0.3 * emotional_factor)
        
        # Determine bias category
        bias_category = "Neutral"
        if bias_score > 0.65:
            bias_category = "Highly Biased"
        elif bias_score > 0.3:
            bias_category = "Slightly Biased"
        
        # Add color coding for the bias level
        bias_color = "success"  # green for neutral
        if bias_category == "Slightly Biased":
            bias_color = "warning"  # yellow for slight bias
        elif bias_category == "Highly Biased":
            bias_color = "danger"  # red for high bias
        
        return {
            "bias_score": round(bias_score, 2),
            "bias_category": bias_category,
            "bias_color": bias_color,
            "found_emotional_words": found_words,
            "polarity": round(polarity, 2),
            "subjectivity": round(subjectivity, 2)
        }
    
    except Exception as e:
        logger.error(f"Error analyzing headline: {str(e)}")
        # Return a default neutral result in case of error
        return {
            "bias_score": 0,
            "bias_category": "Error",
            "bias_color": "secondary",
            "found_emotional_words": [],
            "polarity": 0,
            "subjectivity": 0
        }

def get_word_contribution(word):
    """
    Determine which category a biased word belongs to
    
    Args:
        word (str): The word to categorize
        
    Returns:
        str: Category of the word (positive, negative, controversial)
    """
    word = word.lower()
    for category, words in EMOTIONAL_WORDS.items():
        if word in words:
            return category
    return "neutral"