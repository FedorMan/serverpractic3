import tensorflow as tf
import os
import postgresql

def saveProfAnswer(answer):
    db = postgresql.open('pq://postgres:123@localhost:5432/images')
    ins_image_prof_score = db.prepare("update score set expert_answer = $1 WHERE file = $2 and human_string = $3")
    ins_image_prof_score(answer['answer'], answer['file'], answer['human_str'])
    score = {}
    res = db.query("select count(*) from score where expert_answer = 'TP'")
    score['TP'] = res
    res = db.query("select count(*) from score where expert_answer = 'FP'")
    score['FP'] = res
    res = db.query("select count(*) from score where expert_answer = 'FN'")
    score['FN'] = res
    res = db.query("select count(*) from score where expert_answer = 'TN'")
    score['TN'] = res
    return score

def getResultData():
    db = postgresql.open('pq://postgres:123@localhost:5432/images')
    res = db.query("select file, human_string, score, expert_answer from score order by file")
    answer = []
    for i in range(0,len(res)):
        if i==0 or res[i]['file'] != res[i-1]['file']:
            a = {}
            score = {}
            a['scores'] = []
            score['human_string'] = res[i][1]
            score['score'] = res[i][2]
            score['expert'] = res[i][3]
            a['scores'].append(score)
            a['file'] = res[i][0]
            answer.append(a)
        else:
            score = {}
            score['human_string'] = res[i][1]
            score['score'] = res[i][2]
            score['expert'] = res[i][3]
            a['scores'].append(score)
    return answer

def classificate_all(folder):
    for file in os.listdir(folder):
        print(os.path.join(folder, file))
        neuron_network_classification(os.path.join(folder, file), file)

def neuron_network_classification(image_path, file):
    # считывает файл image_data
    image_data = tf.gfile.FastGFile(image_path, 'rb').read()

    # загружает выбранный файл и удаляет символ разрыва строки
    label_lines = [line.rstrip() for line in tf.gfile.GFile("untitled\\retrained_labels.txt")]

    # получить граф из файла
    with tf.gfile.FastGFile("untitled\\retrained_graph.pb", 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')

    # загружает image_data как входные данные и отображает первые предположения
    with tf.Session() as sess:
        softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
        predictions = sess.run(softmax_tensor, {'DecodeJpeg/contents:0': image_data})

    # сортирует категории после первых предположений в порядке роста уверенности
    top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

    db = postgresql.open('pq://postgres:123@localhost:5432/images')
    ins_image_score = db.prepare("INSERT INTO score (file,human_string,score) VALUES ($1, $2, $3)")

    for node_id in top_k[:5]:
        human_string = label_lines[node_id]
        score = predictions[0][node_id]
        if score > 0.1:
            ins_image_score(file, human_string, score)
            print('%s (score = %.5f)' % (human_string, score))

