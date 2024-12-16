class InsightGenerator:
    def generate_insights(self, summaries):
        combined_text = "\n".join(summaries)
        
        prompt = f"""
        Based on these summaries of AWS re:Invent industry-related sessions:
        {combined_text}
        
        Please provide:
        1. Key themes and trends
        2. Major announcements
        3. Industry focus areas
        4. Notable use cases
        5. Overall insights and conclusions
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant that analyzes AWS re:Invent content."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content 