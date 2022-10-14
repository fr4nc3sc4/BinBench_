import json
import math
from wordsegment import load, segment
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import sys
import itertools
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

types = {
    'pointer': 0,
    'float': 1,
    'char': 2,
    'int': 3,
    'enum': 4,
    'struct': 5,
    'union': 6,
    'void': 7,
    'dummy': 8
}
task_list=['binary_similarity', 'function_search', 'function_naming', 'compiler_provenance', 'signature_recovery']

def flatten_array_name(pretokenized_name):
    # flatten the array of the pretokenized name
    return [tok for sublst in pretokenized_name for tok in sublst]


def snake_case(func_name):
    match = list(filter(None,func_name.split("_")))
    return match

def convert_name(func_names):
    ws = load()
    for func_name in func_names:
        if isinstance(func_name, list):
            func_name = ' '.join(func_name)
        ws = snake_case(func_name)
        ret_func_names = flatten_array_name([segment(word) for word in ws])

    return ret_func_names


def eval_compiler_provenance(gold_datapoints, guess_datapoints):
    try:
        gold = [1 if "gcc" in gold_datapoint["compiler"] else 0 for gold_datapoint in gold_datapoints]

        guess = []
        for guess_datapoint in guess_datapoints:
            if "gcc" in guess_datapoint["compiler"]:
                guess.append(1)
            elif "clang" in guess_datapoint["compiler"]:
                guess.append(0)
            else:
                # wrong entry ...
                position = len(guess)
                # pick the value in gold, and use the opposite value
                if gold[position] == 1:
                    val = 0
                else:
                    val = 1
                guess.append(val)
    except:
        print("key error: please check your submission")
        exit()

    result = [
        {
            chosen_task: {
                'Accuracy': accuracy_score(gold, guess),
                'Precision': precision_score(gold, guess),
                'Recall': recall_score(gold, guess),
                'F1 Score': f1_score(gold, guess),
            }
        }
    ]
    print(result)
    return result


def eval_function_naming(gold_datapoints, guess_datapoints):
    try:
        gold = [gold_datapoint["split_name"] for gold_datapoint in gold_datapoints]
        guess = [guess_datapoint["name"] for guess_datapoint in guess_datapoints]
        convert_name(guess)
    except Exception as e:
        print(str(e))
        print("key error: please check your submission")
        exit()

    avg_precision = 0.0
    avg_recall = 0.0
    avg_f1 = 0.0
    avg_bleu = 0.0

    for gold_tokenized_name, guess_tokenized_name in zip(gold, guess):
        num_gold_tokens = len(gold_tokenized_name)
        num_guess_tokens = len(guess_tokenized_name)

        if num_gold_tokens == 0 and num_guess_tokens == 0:
            precision = 1
            recall = 1
            f1 = 1
            bleu = 1

        elif (num_gold_tokens > 0 and num_guess_tokens == 0) or (num_gold_tokens == 0 and num_guess_tokens > 0):
            precision = 0
            recall = 0
            f1 = 0
            bleu = 0

        else:
            name_score = 0
            for token in guess_tokenized_name:
                name_score = name_score + 1 if token in gold_tokenized_name else name_score
            precision = name_score / len(guess_tokenized_name)
            recall = name_score / len(gold_tokenized_name)
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

            if len(gold_tokenized_name) <= 6:
            ######### to add references, we add also permutations. However, since this process is CPU consuming,
            # we limit it to names composed by 6 tokens
                gold_reference = [list(permutation) for permutation in itertools.permutations(gold_tokenized_name)]
            else:
                gold_reference = [gold_tokenized_name]
            weights = [float(1./(len(gold_tokenized_name))) for i in range(len(gold_tokenized_name))]
            chencherry = SmoothingFunction()
            bleu = sentence_bleu(gold_reference, guess_tokenized_name, weights, smoothing_function=chencherry.method2)


        avg_precision += precision
        avg_recall += recall
        avg_f1 += f1
        avg_bleu += bleu

    result = [
        {
            chosen_task: {
                'Precision': avg_precision / len(gold),
                'Recall': avg_recall / len(gold),
                'F1 Score': avg_f1 / len(gold),
                'BLEU Score': avg_bleu / len(gold)
            }
        }
    ]

    print(result)
    return result


def eval_signature_recovery(gold_datapoints, guess_datapoints):
    try:
        gold = [gold_datapoint["parameters"] for gold_datapoint in gold_datapoints]
        guess = [guess_datapoint["parameters"] for guess_datapoint in guess_datapoints]
    except:
        print("key error: please check your submission")
        exit()

    gold_encoding = []
    guess_encoding = []

    for gold_signature, guess_signature in zip(gold, guess):
        gold_sig_encoding = [types[param['type']] for param in gold_signature]
        guess_sig_encoding = [types[param['type']] for param in guess_signature]

        if len(gold_sig_encoding) == 0:
            gold_sig_encoding = [types['void']]
        if len(guess_sig_encoding) == 0:
            guess_sig_encoding = [types['void']]

        gold_sig_encoding_len = len(gold_sig_encoding)
        guess_sig_encoding_len = len(guess_sig_encoding)

        mismatch = gold_sig_encoding_len - guess_sig_encoding_len

        if (mismatch > 0):
            padding = [types['dummy']] * mismatch
            guess_sig_encoding.extend(padding)

        elif (mismatch < 0):
            padding = [types['dummy']] * abs(mismatch)
            gold_sig_encoding.extend(padding)

        gold_encoding.extend(gold_sig_encoding)
        guess_encoding.extend(guess_sig_encoding)

    result = [
        {
            chosen_task: {
                'Accuracy': accuracy_score(gold_encoding, guess_encoding),
                'Precision': precision_score(gold_encoding, guess_encoding, average='micro'),
                'Recall': recall_score(gold_encoding, guess_encoding, average='micro')
            }
        }
    ]

    print(result)
    return result


def eval_binary_similarity(gold_datapoints, guess_datapoints):
    try:
        gold = [1.0 if gold_datapoint["similarity"] == "+1" else 0.0 for gold_datapoint in gold_datapoints]
        guess = []
        for guess_datapoint in guess_datapoints:
            if "+1" in guess_datapoint["similarity"]:
                guess.append(1)
            elif "-1" in guess_datapoint["similarity"]:
                guess.append(0)
            else:
                # wrong entry ...
                position = len(guess)
                # pick the value in gold, and use the opposite value
                if gold[position] == 1:
                    val = 0
                else:
                    val = 1
                guess.append(val)

    except:
        print("key error: please check your submission")
        exit()

    result = [
        {
            chosen_task: {
                'ROC AUC': round(roc_auc_score(gold, guess), 3)
            }
        }
    ]

    print(result)
    return result


def eval_function_search(gold_datapoints, guess_datapoints, top_num):
    try:
        gold = [gold_datapoint["similars"] for gold_datapoint in gold_datapoints]
        guess = [guess_datapoint["similars"][:top_num] for guess_datapoint in guess_datapoints]
    except:
        print("key error: please check your submission")
        exit()

    try:
        for elem in guess:
            assert(len(elem) == top_num)
    except:
        print("similars mismatch error: please check your submission")
        exit()

    avg_precision = 0.0
    avg_recall = 0.0
    avg_f1 = 0.0
    avg_ndcg = 0.0

    for gold_tokenized_similars, guess_tokenized_similars in zip(gold, guess):

        correct_guess = 0
        ndcg_guess = 0
        ideal_ndcg = 0

        i = 1

        for token in guess_tokenized_similars:
            correct_guess = correct_guess + 1 if token in gold_tokenized_similars else correct_guess
            ndcg_guess = ndcg_guess + (1 / math.log((1 + i), 2)) if token in gold_tokenized_similars else ndcg_guess
            ideal_ndcg = ideal_ndcg + (1 / math.log((1 + i), 2))

            i += 1

        precision = correct_guess / len(guess_tokenized_similars)
        recall = correct_guess / len(gold_tokenized_similars)
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        ndcg = ndcg_guess / ideal_ndcg

        avg_precision += precision
        avg_recall += recall
        avg_f1 += f1
        avg_ndcg += ndcg

    result = [
        {
            chosen_task: {
                'Precision': avg_precision / len(gold),
                'Recall': avg_recall / len(gold),
                'F1 Score': avg_f1 / len(gold),
                'nDCG Score': avg_ndcg / len(gold),
            }
        }
    ]

    print(result)
    return result


def load_datapoints(test_annotation_file, user_submission_file):


    gold_datapoints = []
    guess_datapoints = []

    with open(test_annotation_file) as gold:
        for gold_line in gold:
            gold_datapoints.append(json.loads(gold_line))
    with open(user_submission_file) as guess:
        for guess_line in guess:
            guess_datapoints.append(json.loads(guess_line))

    #if len(gold_datapoints) != len(guess_datapoints):
        #print("key error: incomplete submission file (missing datapoints!)")
        #exit()

    return gold_datapoints, guess_datapoints


def evaluate(test_annotation_file, user_submission_file, phase_codename, **kwargs):
    output = {}
    gold_datapoints, guess_datapoints = load_datapoints(test_annotation_file, user_submission_file)

    if phase_codename == "compiler_provenance":
        result = eval_compiler_provenance(gold_datapoints, guess_datapoints)
    elif phase_codename == "function_naming":
        result = eval_function_naming(gold_datapoints, guess_datapoints)
    elif phase_codename == "signature_recovery":
        result = eval_signature_recovery(gold_datapoints, guess_datapoints)
    elif phase_codename == "binary_similarity":
        result = eval_binary_similarity(gold_datapoints, guess_datapoints)
    elif phase_codename == "function_search":
        result = eval_function_search(gold_datapoints, guess_datapoints, 20)

    output["result"] = result

    return output


if __name__ == '__main__':
    groundtruth, predictions, chosen_task = sys.argv[1:]

    if chosen_task not in task_list:
        print("SCRIPT USAGE:\npython evaluation_script.py groundtruth_file.jsonl predictions_file.jsonl chosen_task")
    else:
        evaluate(groundtruth,predictions,chosen_task)

