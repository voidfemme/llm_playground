# Prompt Engineering

## Prompt Development Lifecycle

1. Key Success Areas
    - **Performance and accuracy:** How well does the model need to perform on the task?
    - **Latency:** What is the acceptable response time for the model? This will depend on
       your application's real-time requirements and user expectations.
    - **Price:** What is your budget for running the model? Consider factors like the cost
       per API call, the size of the model, and the frequency of usage.
2. **Develop Test Cases:**
    - Include typical examples and edge cases to ensure the prompt is robust
3. **Engineer the preliminary prompt:**
    - Task Definition
    - Characteristics of a Good response
    - Necessary context for Claude.
    - Examples of canonical inputs and outputs for Claude to follow.
4. **Test Prompt against test cases:**
    - Carefully evaluate the model's responses against expected outputs and success
       criteria.)
    - Use a consistent grading rubric, whether human eval, comparison to answer key, or
      even another instance of Claude's judgement based on a rubric. The key is to have a
      systematic way to assess performance.
5. **Refine Prompt:**
    - Based on the results from step 4, iteratively refine the prompt to improve
      performance
    - Add Clarifications, Examples, or Constraints
    - Careful to not overly optimize for a narrow set of inputs, as this can lead to
      overfitting and poor generalization
6. **Ship the polished prompt:**
    - Monitor the model's performance in the wild and be prepared to make further
      refinements as needed.

## Prompt Engineering Techniques

1. **Be clear and direct.** Provide clear instructions and context to guide Claude's
   responses.
2. **Use examples.** Include examples in your prompts to illustrate the desired output
   format or style
3. **Give Claude a role.** Prime Claude to inhabit a specific role (like that of an
   expert) in order to increase performance for your use case
4. **Use XML tags.** Incorporate XML tags to structure prompts and responses for greater
   clarity.
5. **Chain prompts.** Divide complex tasks into smaller, manageable steps for better
   results.
6. **Let Claude think.** Encourage step-by-step thinking to improve the quality of
   Claude's output
7. **Prefill Claude's response.** Start Claude's response with a few words to guide its
   output in the desired direction.
8. **Control output format.** Specify the desired output format to ensure consistency and
   readability.
9. **Ask Claude for rewrites.** Request revisions based on a rubric to get Claude to
   iterate and improve its output
10. **Long Context Window Tips:** Optimize prompts that take advantage of Claude's longer
    context windows.
