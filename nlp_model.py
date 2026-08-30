from intents import intents

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


training_sentences = []
training_labels = []

for intent, sentences in intents.items():
    for sentence in sentences:
        training_sentences.append(sentence)
        training_labels.append(intent)


vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2)
)

X = vectorizer.fit_transform(training_sentences)

model = LogisticRegression(
    max_iter=1000
)

model.fit(X, training_labels)


def predict_intent(message):

    message_vector = vectorizer.transform([message])

    prediction = model.predict(message_vector)

    return prediction[0]


if __name__ == "__main__":

    print("======================================")
    print("       E-COMMERCE NLP MODEL")
    print("======================================")

    print("NLP model trained successfully!")
    print("Type 'bye' to stop.")
    print()

    while True:

        user = input("You: ").strip()

        if user.lower() == "bye":
            print("Model stopped.")
            break

        intent = predict_intent(user)

        print("Detected Intent:", intent)
        print()