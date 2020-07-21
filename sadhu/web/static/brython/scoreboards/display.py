from browser import window, document, timer, ajax
import datetime
import javascript
import random

fabric = window.fabric


class ScoreBoard:
    def __init__(self, name='scoreboard', width=800, height=600, data_url=''):
        self.name = name
        self.width = width
        self.height = height
        self.data_url = data_url

        self.canvas = fabric.Canvas.new(
                self.name,
                {
                    'width': width,
                    'height': height,
                    'backgroundColor': 'black',
                    'selectable': False,
                })
        self.running = True
        self.data = {}
        self.widgets = {}


    def display_text(self, data):
        return f'{data["name"]}\n{data["score"]:.02f}/{data["max_score"]}({data["complete"]}/{data["challenges"]})'


    def draw(self, key, data):
        colors = ['#E63F30', '#D4ACA7', '#EB998D', '#F27F5C', '#E0651D', '#D49D7B',
                  '#EBCCCC', '#E5B513', '#FCF2A7', '#E6D85A', '#F0D030', '#DFF890',
                  '#EAF0C2', '#BDD13B', '#C1F55B', '#12DB9B', '#066B54', '#18A18A',
                  '#7BC7C1', '#06B8CC', '#06AEC4', '#8DC3D9', '#03669C', '#207EE8',
                  '#8EAAE8', '#69508A', '#EDC0E9', '#BA6EA1', '#D957A7', '#E8157E']

        min_top = self.height - 150
        min_left = 10
        
        max_top = self.height - 30
        max_left = self.width - 50

        y = random.randrange(min_top, max_top)
        x = random.randrange(min_left, max_left)


        if data['max_score'] - data['score'] == 0:
            y = 0
        elif data['score'] != 0:
            y = data['score'] * (self.height / data['max_score'])

        color = random.choice(colors)
        text = fabric.Text.new(
            self.display_text(data),
            {
                'fontSize': 16,
                'left': x,
                'top': y,
                'fill': color,
                'textAlign': 'center',
                'fontFamily': 'Comic Sans',
                'selectable': False,
            }
        )
        self.widgets[key] = data

        self.canvas.add(text)


    def update(self, key, data):
        print('update')

        text = self.widgets[key]
        text.setText(self.display_text())

        y = data['score'] * (self.height / data['max_score'])
        text.set(
            {
                'top': y
            }
        )


    def stop(self):
        self.running = False


    def on_ajax_complete(self, request):
        data = javascript.JSON.parse(request.text)
        for k, d in data.items():
            old_data = self.data.get(k)
            if not old_data:
                self.data[k] = d
                self.draw(k, d)

            elif old_data['score'] != d['score']:
                self.update(k, d)
                self.data[k] = d


    def get_student_scores(self):
        print('weakup', datetime.datetime.now())
        request = ajax.get(
                self.data_url,
                oncomplete=self.on_ajax_complete)


    def run(self):
        self.get_student_scores()
        timer.set_interval(self.get_student_scores, 60000)



