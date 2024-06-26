from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import Post,Comment
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required




def post_list(request):
    query = request.GET.get('q')
    if query:
        posts = Post.objects.filter(title__icontains=query, published_date__lte=timezone.now()).order_by('published_date')
        if not posts:
            message = "No such blog found."
            return render(request, 'blog/post_list.html', {'message': message})
    else:
        posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})

@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('post_list')

def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/add_comment_to_post.html', {'form': form})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('post_detail', pk=comment.post.pk)


from django.shortcuts import render
import google.generativeai as genai
@login_required
def new_post(request):
    if request.method == "POST":
        subject = request.POST.get('subject', '')
        if subject:
            # Configure the Generative AI with your API key
            genai.configure(api_key="key")

            # Set up model generation configuration and safety settings
            generation_config = {
                "temperature": 0.7,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            }
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
            ]

            # Initialize the GenerativeModel
            model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                          generation_config=generation_config,
                                          safety_settings=safety_settings)

            # Start a conversation with the model
            convo = model.start_chat(history=[
                {
    "role": "user",
    "parts": ["i need to make a blog generator based on my prompt"]
  },
  {
    "role": "model",
    "parts": ["**Blog Generator Based on Prompt**\n\n**Requirements:**\n\n* Input: A text prompt\n* Output: A fully generated blog post based on the prompt\n\n**Steps:**\n\n**1. Natural Language Processing (NLP)**\n\n* Use an NLP library (e.g., spaCy or NLTK) to analyze the prompt:\n    * Extract keywords and phrases\n    * Identify the topic and main idea\n    * Determine the target audience and writing style\n\n**2. Content Creation**\n\n* **Headline:** Create a catchy and relevant headline that captures the essence of the prompt.\n* **Introduction:** Provide a brief overview of the topic, introducing the main idea and hooking the reader.\n* **Body:** Develop the main points of the blog post, using evidence, examples, and supporting arguments.\n* **Call-to-Action (CTA):** If appropriate, include a CTA at the end to encourage readers to take a specific action.\n\n**3. Formatting and Structure**\n\n* **Length:** Determine the optimal length of the blog post based on the topic and target audience.\n* **Paragraphs:** Break up the content into logical paragraphs with clear topic sentences.\n* **Headings:** Use headings to organize the content and make it easy to skim.\n* **Images and Videos:** Include relevant images or videos to enhance the reader's experience.\n\n**4. Tone and Style**\n\n* **Voice:** Choose a consistent voice for the blog post, whether it's formal, conversational, or humorous.\n* **Tone:** Adjust the tone to match the prompt and target audience, ensuring it's engaging and appropriate.\n\n**5. Proofreading and Editing**\n\n* **Grammar and Spelling:** Use a grammar and spell checker to ensure the blog post is error-free.\n* **Clarity and Conciseness:** Review the content to ensure it's clear, concise, and easy to understand.\n* **Flow:** Check that the blog post has a logical flow and transitions smoothly between sections.\n\n**Example Output:**\n\n**Prompt:** The benefits of mindfulness meditation\n\n**Output Blog Post:**\n\n**Headline:** **Unlock Your Inner Peace: The Transformative Benefits of Mindfulness Meditation**\n\n**Introduction:**\n\nIn today's fast-paced world, mindfulness meditation has emerged as a powerful tool to enhance our well-being and reduce stress. This practice involves training your mind to focus on the present moment, without judgment. This blog post will explore the numerous benefits of mindfulness meditation, from reducing anxiety to improving cognitive function.\n\n**Body:**\n\n* **Reduces Anxiety and Stress:** Mindfulness meditation has been shown to effectively reduce anxiety and stress levels. By focusing on the present moment, we can let go of worries about the past or future, and cultivate a sense of calm and relaxation.\n* **Improves Cognitive Function:** Regular mindfulness meditation practice has been linked to improved cognitive function, including enhanced attention, memory, and problem-solving skills. It helps strengthen neural pathways in the brain that are responsible for these cognitive abilities.\n* **Enhances Emotional Regulation:** Mindfulness meditation teaches us to observe our emotions without judgment. This allows us to develop greater emotional awareness and regulation skills, reducing emotional reactivity and improving our ability to cope with difficult emotions.\n* **Promotes Self-Compassion:** Mindfulness meditation encourages us to treat ourselves with kindness and acceptance. By observing our thoughts and feelings without judgment, we can cultivate a greater sense of self-compassion and reduce self-criticism.\n\n**Conclusion:**\n\nMindfulness meditation is a transformative practice that offers a wide range of benefits for our mental, emotional, and overall well-being. Whether you're seeking to reduce stress, improve cognitive function, or cultivate greater self-compassion, mindfulness meditation can be a powerful tool to enhance your life. By embracing this practice, you can unlock your inner peace and experience the transformative benefits it has to offer."]
  },
  {
    "role": "user",
    "parts": ["the content of the blog will generate in single paragraph"]
  },
  {
    "role": "model",
    "parts": ["**Single-Paragraph Blog Generator Based on Prompt**\n\n**Requirements:**\n\n* Input: A text prompt\n* Output: A single paragraph of blog content based on the prompt\n\n**Steps:**\n\n**1. Natural Language Processing (NLP)**\n\n* Use an NLP library (e.g., spaCy or NLTK) to analyze the prompt:\n    * Extract keywords and phrases\n    * Identify the topic and main idea\n    * Determine the target audience and writing style\n\n**2. Content Creation**\n\n* **Topic Sentence:** Create a strong topic sentence that captures the essence of the prompt and introduces the main idea.\n* **Supporting Sentences:** Develop 2-3 supporting sentences that provide evidence, examples, or arguments to support the main idea.\n* **Concluding Sentence:** Summarize the main points and restate the thesis in a concise and impactful way.\n\n**3. Formatting and Structure**\n\n* **Length:** Aim for a paragraph length of around 150-250 words.\n* **Clarity and Conciseness:** Ensure the paragraph is easy to understand and free of unnecessary details.\n* **Flow:** Use transitions and connecting words to create a smooth flow between sentences.\n\n**4. Tone and Style**\n\n* **Voice:** Choose a consistent voice for the paragraph, whether it's formal, conversational, or humorous.\n* **Tone:** Adjust the tone to match the prompt and target audience, ensuring it's engaging and appropriate.\n\n**5. Proofreading and Editing**\n\n* **Grammar and Spelling:** Use a grammar and spell checker to ensure the paragraph is error-free.\n* **Clarity and Conciseness:** Review the content to ensure it's clear, concise, and easy to understand.\n* **Flow:** Check that the paragraph has a logical flow and transitions smoothly between sentences.\n\n**Example Output:**\n\n**Prompt:** The benefits of mindfulness meditation\n\n**Output Paragraph:**\n\nMindfulness meditation offers numerous benefits for our well-being. It reduces anxiety and stress by focusing our attention on the present moment, letting go of worries about the past or future. Regular practice has also been linked to improved cognitive function, including enhanced attention, memory, and problem-solving skills. Additionally, mindfulness meditation promotes emotional regulation by teaching us to observe our emotions without judgment, leading to greater emotional awareness and resilience. By embracing this practice, we can cultivate greater self-compassion and reduce self-criticism. Ultimately, mindfulness meditation empowers us to unlock our inner peace and experience a more fulfilling and balanced life."]
  },
  {
    "role": "user",
    "parts": ["and avoid the sub headings make it in single paragraph"]
  },
  {
    "role": "model",
    "parts": ["**Single-Paragraph Blog Generator Without Subheadings Based on Prompt**\n\n**Requirements:**\n\n* Input: A text prompt\n* Output: A single paragraph of blog content based on the prompt, without subheadings\n\n**Steps:**\n\n**1. Natural Language Processing (NLP)**\n\n* Use an NLP library (e.g., spaCy or NLTK) to analyze the prompt:\n    * Extract keywords and phrases\n    * Identify the topic and main idea\n    * Determine the target audience and writing style\n\n**2. Content Creation**\n\n* **Topic Sentence:** Create a strong topic sentence that captures the essence of the prompt and introduces the main idea.\n* **Body Paragraph:** Develop a cohesive paragraph that covers the main points related to the prompt. Use evidence, examples, and arguments to support your claims.\n* **Concluding Sentence:** Summarize the main points and restate the thesis in a concise and impactful way.\n\n**3. Formatting and Structure**\n\n* **Length:** Aim for a paragraph length of around 150-250 words.\n* **Clarity and Conciseness:** Ensure the paragraph is easy to understand and free of unnecessary details.\n* **Flow:** Use transitions and connecting words to create a smooth flow between sentences.\n\n**4. Tone and Style**\n\n* **Voice:** Choose a consistent voice for the paragraph, whether it's formal, conversational, or humorous.\n* **Tone:** Adjust the tone to match the prompt and target audience, ensuring it's engaging and appropriate.\n\n**5. Proofreading and Editing**\n\n* **Grammar and Spelling:** Use a grammar and spell checker to ensure the paragraph is error-free.\n* **Clarity and Conciseness:** Review the content to ensure it's clear, concise, and easy to understand.\n* **Flow:** Check that the paragraph has a logical flow and transitions smoothly between sentences.\n\n**Example Output:**\n\n**Prompt:** The benefits of mindfulness meditation\n\n**Output Paragraph:**\n\nMindfulness meditation offers a multitude of benefits for our mental and emotional well-being. By focusing our attention on the present moment, it reduces anxiety and stress, allowing us to let go of worries about the past or future. Regular practice has also been shown to enhance cognitive function, including attention, memory, and problem-solving skills. Moreover, mindfulness meditation promotes emotional regulation by teaching us to observe our emotions without judgment, leading to greater emotional awareness and resilience. It also fosters self-compassion and reduces self-criticism. Ultimately, embracing mindfulness meditation empowers us to cultivate inner peace, reduce suffering, and live more fulfilling and balanced lives."]
  },
])


            # Generate content based on the provided subject
            convo.send_message(subject)
            generated_content = convo.last.text

            # Save the generated content in a new Post instance
            post_form = PostForm({'title': subject, 'text': generated_content})
            if post_form.is_valid():
                post = post_form.save(commit=False)  # Don't save yet, wait to set author
                post.author = request.user  # Assuming you have a user associated with this post
                post.save()
                return redirect('post_detail', pk=post.pk)

    return render(request, 'blog/generate.html', {'generated_content': None})
