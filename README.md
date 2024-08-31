The application is a blog.

It is hosted [here](https://rxjourney.com.ng).

It is built with Django.

This is the server for the above linked website.

The Server -

1. retrieves a post by its slug, selects up to four random other posts, and returns their details as a JSON response with truncated content for preview.
2. sends an HTML email notification about a new blog post to all subscribers using the Brevo API, handling errors if the API key is missing or if the email sending fails.
3. creates a time-stamped token for email verification using Django's TimestampSigner. Sends an HTML email with a confirmation link to the provided email address using the Brevo API, handling errors if the API key is missing or if the email sending fails.
4. attempts to verify the time-stamped token to confirm a subscription, creating a new subscriber if the email doesn't already exist, and returns appropriate JSON responses based on the outcome. If the token is invalid or expired, a JSON response with an error message is returned.
5. returns the total number of subscribers; performs a search query on blog post titles and content, returning matching results in JSON format.

And more
