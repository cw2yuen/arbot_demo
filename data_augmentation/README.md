# Data Augmentation for Arbo Dental Care AI Agent

This system allows you to augment the AI agent's knowledge base with commonly asked dental questions and answers that may not be covered on the website.

## 📁 Files

- **`dental_qa_template.csv`** - Template CSV file with pre-filled common dental Q&A
- **`merge_qa_data.py`** - Script to merge CSV data with existing JSON
- **`README.md`** - This documentation file

## 🚀 How to Use

### Step 1: Customize the CSV Template

1. **Open** `dental_qa_template.csv` in Excel, Google Sheets, or any CSV editor
2. **Edit** the existing Q&A pairs to match Arbo Dental Care's specific policies
3. **Add** new Q&A pairs based on common patient questions
4. **Save** the file

### Step 2: CSV Format

The CSV has 5 columns:

| Column | Description | Example |
|--------|-------------|---------|
| `question` | The patient's question | "What are your office hours?" |
| `answer` | Your detailed answer | "Our office hours are Monday to Friday..." |
| `category` | Question category | "hours", "insurance", "treatments" |
| `source` | Data source | "manual" (for manually added data) |
| `priority` | Importance level | "high", "medium", "low" |

### Step 3: Run the Merger

```bash
python data_augmentation/merge_qa_data.py
```

This will:
- Load your CSV data
- Merge it with existing website data
- Create `arbo_dental_data_augmented.json`
- Show analysis of the merged data

### Step 4: Rebuild Knowledge Base

```bash
python data_preparation/knowledge_base.py
```

## 📋 Pre-filled Categories

The template includes Q&A for these categories:

### **High Priority**
- **Hours** - Office hours and availability
- **Insurance** - Coverage and payment options
- **Emergency** - Emergency procedures and contacts
- **Appointments** - Scheduling and preparation
- **Preventive** - Basic dental care questions
- **Comfort** - Dental anxiety and comfort options

### **Medium Priority**
- **Treatments** - Specific dental procedures
- **Orthodontics** - Braces and Invisalign
- **Pediatric** - Children's dental care
- **Cosmetic** - Whitening and appearance
- **Payment** - Financing and payment plans

### **Low Priority**
- **General** - Miscellaneous dental topics

## ✏️ Customization Tips

### **Adding New Questions**
1. **Think like a patient** - What would someone new to your practice ask?
2. **Use natural language** - Write questions as patients would ask them
3. **Be specific** - Include details about your practice's policies
4. **Consider seasonal questions** - Holiday hours, summer appointments, etc.

### **Writing Good Answers**
1. **Be comprehensive** - Answer the question fully
2. **Include contact info** - Always mention how to reach you
3. **Be reassuring** - Address common concerns and fears
4. **Use your voice** - Match your practice's tone and style

### **Categorization**
- **High Priority**: Essential information every patient needs
- **Medium Priority**: Important but not urgent information
- **Low Priority**: Nice-to-know information

## 🔄 Workflow

```
1. Edit CSV Template
   ↓
2. Run Merger Script
   ↓
3. Rebuild Knowledge Base
   ↓
4. Test AI Responses
   ↓
5. Iterate and Improve
```

## 📊 Example Q&A Entry

```csv
"What if I'm running late for my appointment?","Please call us as soon as possible if you're running late. We'll do our best to accommodate you, but if you're more than 15 minutes late, we may need to reschedule to avoid affecting other patients. We understand emergencies happen and will work with you.","appointments","manual","medium"
```

## 🧪 Testing Your Additions

After merging and rebuilding:

1. **Restart your chatbot**
2. **Ask the new questions** you added
3. **Check debug mode** to see if the AI finds your Q&A data
4. **Verify responses** match your intended answers

## 💡 Best Practices

### **Question Writing**
- Use natural, conversational language
- Include variations of the same question
- Think about different ways patients might phrase things

### **Answer Writing**
- Be specific to Arbo Dental Care
- Include relevant contact information
- Address common follow-up questions
- Keep answers concise but complete

### **Maintenance**
- Update Q&A regularly based on patient feedback
- Add new questions as they arise
- Remove outdated information
- Keep categories organized

## 🚨 Common Issues

### **CSV Format Problems**
- Ensure proper comma separation
- Use quotes around text with commas
- Check for extra spaces or special characters

### **Merging Errors**
- Verify CSV file path is correct
- Ensure existing JSON file exists
- Check file permissions

### **Knowledge Base Issues**
- Clear old knowledge base before rebuilding
- Check for duplicate entries
- Verify data structure consistency

## 🔮 Future Enhancements

- **Automated Q&A extraction** from patient communications
- **Feedback loop** to improve answers based on AI performance
- **Multi-language support** for Portuguese, Spanish, Vietnamese
- **Seasonal Q&A** that automatically updates
- **Integration** with appointment booking system

---

**Need Help?** Contact the development team or check the main project README for additional support.


