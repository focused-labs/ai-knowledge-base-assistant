import csv

from assistant import Assistant


def run_accuracy_test():
    assistant = Assistant("human")

    with open('accuracy_test_questions.txt', 'r') as file:
        questions = [line.strip() for line in file if line.strip()]

    responses = []
    for question in questions:
        response = assistant.process_question(question=question, in_new_thread=True)
        responses.append(response)

    with open('accuracy_test_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(
            ['Timestamp', 'Question', 'Answer', 'Error Message', 'Accuracy(1 - 5 where 5 is the best)', 'Comments'])

        for response in responses:
            csvwriter.writerow(response)
