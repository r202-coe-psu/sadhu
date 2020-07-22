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
                    'renderOnAddRemove': False,
                })
        self.running = True
        self.data = {}
        self.widgets = {}
        self.animate_time = 30000

        self.min_top = 10
        self.min_left = 50
        
        self.max_top = self.height - 50
        self.max_left = self.width - 50




    def display_text(self, data):
        return f'{data["name"]}\n{data["score"]:.02f}/{data["max_score"]} ({data["complete"]}/{data["challenges"]})'


    def draw(self, key, data):
        colors = ['#E63F30', '#D4ACA7', '#EB998D', '#F27F5C', '#E0651D', '#D49D7B',
                  '#EBCCCC', '#E5B513', '#FCF2A7', '#E6D85A', '#F0D030', '#DFF890',
                  '#EAF0C2', '#BDD13B', '#C1F55B', '#12DB9B', '#066B54', '#18A18A',
                  '#7BC7C1', '#06B8CC', '#06AEC4', '#8DC3D9', '#03669C', '#207EE8',
                  '#8EAAE8', '#69508A', '#EDC0E9', '#BA6EA1', '#D957A7', '#E8157E']

        x = random.randrange(self.min_left, self.max_left)
        y = self.max_top

        if data['max_score'] - data['score'] == 0:
            y = self.min_top
        elif data['score'] != 0:
            y = self.height - (data['score'] * (self.height / data['max_score']))

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
        self.widgets[key] = text

        self.canvas.add(text)
        self.animate(text, data)


    def animate(self, obj, data):

        padding = (self.max_top-self.min_top) / (data['max_score']+1)
        max_level_top = self.max_top - int(data['score'] * padding)
        min_level_top = self.max_top - int((data['score']+1) * padding)

        animate_time = random.randrange(1000, self.animate_time)
        

        if obj.left < -10:
            obj.set({
                'left': self.width + 10
                })

        xrand = random.randrange(0, 100)

        obj.animate('left', f'-={xrand}', {
            'onChange': self.canvas.renderAll.bind(self.canvas),
            'duration': animate_time,
            'easing': fabric.util.ease.easeOutBounce,
            })


        yrand = random.randrange(min_level_top, max_level_top)
        obj.animate('top', yrand, {
            # 'onChange': self.canvas.renderAll.bind(self.canvas),
            'duration': animate_time,
            'easing': fabric.util.ease.easeOutBounce,
            })

        z = random.randrange(0, 10)
        obj.moveTo(z)


    def update(self, key, data):
        obj = self.widgets[key]
        obj.set(
            {
                'text': self.display_text(data)
            }
        )

        self.animate(obj, data)


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


    def schedule_animate(self):
        for k, obj in self.widgets.items():
            self.animate(obj, self.data[k])

        self.canvas.renderAll()


    def run(self):
        self.get_student_scores()
        timer.set_interval(self.get_student_scores, 60000)
        timer.set_interval(self.schedule_animate, self.animate_time)



