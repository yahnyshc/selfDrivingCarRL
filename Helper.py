import matplotlib.pyplot as plt
from IPython.display import clear_output, display

plt.ion()

def plot(scores, mean_scores):
    clear_output(wait=True)
    plt.clf()
    plt.title("Training...")
    plt.xlabel('Number of Games')
    plt.ylabel('Score')
    plt.plot(scores, label='Scores')
    plt.plot(mean_scores, label='Mean Scores')
    plt.ylim(ymin=0)
    plt.legend()
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    display(plt.gcf())
    plt.pause(0.001)  # Add a brief pause to update the figure