from flask import Flask, render_template, request
from wtforms import Form, FloatField, SelectField, validators
import time
import os

## import computation function for bootstrapping app
## and black-scholes option pricing app
from compute.compute import bootstrapping_col, text2data_col, blsprice

## import bokeh for plots
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.models import CustomJS, ColumnDataSource, Slider
from bokeh.plotting import Figure
from bokeh.embed import components
from bokeh.models.layouts import WidgetBox


app = Flask(__name__)

# directory name of the current path : to be used in bootstrapping page
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

## model

# InputFormBS: For Black-Scholes Option Pricing App
# Form to input value from users

class InputFormBS(Form):
    flag = SelectField(u'Select option type', choices=[('call', 'call'), ('put', 'put')])
    k = FloatField(label='Strike Price', default=1, validators=[validators.InputRequired()])
    s = FloatField(label='Spot Price', default=1, validators=[validators.InputRequired()])
    r = FloatField(label='Interest Rate', default=0.05, validators=[validators.InputRequired()])
    sigma = FloatField(label='Volatility', default=0.20, validators=[validators.InputRequired()])
    t = FloatField(label='Time to Maturity', default=1, validators=[validators.InputRequired()])
    q = FloatField(label='Dividend Yield', default=0.05, validators=[validators.InputRequired()])

## view

# index page
# template file : index.html
@app.route('/')
def index():
    return render_template('index.html')

# Black-Scoles Model Option Pricing Page
# template file : bsm.html
@app.route('/bsm/', methods=['GET', 'POST'])
def bsm():
    form = InputFormBS(request.form)
    if request.method == 'POST' and form.validate():
        result = blsprice(form.k.data, form.s.data, form.r.data, form.sigma.data, form.t.data, form.q.data, form.flag.data)
    else:
        result = None
    return render_template('bsm.html', form=form, price=result)

# Black-Scoles Model Option Pricing Page
# template file : bsm.html
@app.route('/bsm_interactive/', methods=['GET', 'POST'])
def bsm_interactive():

    x = [x/100 for x in range(1, 200)]
    y = [blsprice(1,X,0.05,0.20,1,0,"call") for X in x]
    source = ColumnDataSource(data=dict(x=x, y=y))

    plot = Figure(plot_width=400, plot_height=400)
    plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)

    callbackCall = CustomJS(args=dict(source=source), code="""
        function ndist(z) {
            return (1.0/(Math.sqrt(2*Math.PI)))*Math.exp(-0.5*z);
        }

        function N(z) {
            b1 =  0.31938153;
            b2 = -0.356563782;
            b3 =  1.781477937;
            b4 = -1.821255978;
            b5 =  1.330274429;
            p  =  0.2316419;
            c2 =  0.3989423;
            a=Math.abs(z);
            if (a>6.0) {return 1.0;}
            t = 1.0/(1.0+a*p);
            b = c2*Math.exp((-z)*(z/2.0));
            n = ((((b5*t+b4)*t+b3)*t+b2)*t+b1)*t;
            n = 1.0-b*n;
            if (z < 0.0) {n = 1.0 - n;}
            return n;
        }

        function black_scholes(call,S,X,r,v,t) {
            // call = Boolean (to calc call, call=True, put: call=false)
            // S = stock prics, X = strike price, r = no-risk interest rate
            // v = volitility (1 std dev of S for (1 yr? 1 month?, you pick)
            // t = time to maturity

            // define some temp vars, to minimize function calls
            var sqt = Math.sqrt(t);
            var Nd2;  //N(d2), used often
            var nd1;  //n(d1), also used often
            var ert;  //e(-rt), ditto
            var delta;  //The delta of the option
            var price; //price of option

            d1 = (Math.log(S/X) + r*t)/(v*sqt) + 0.5*(v*sqt);
            d2 = d1 - (v*sqt);

            if (call) {
                delta = N(d1);
                Nd2 = N(d2);
            } else { //put
                delta = -N(-d1);
                Nd2 = -N(-d2);
            }

            ert = Math.exp(-r*t);
            nd1 = ndist(d1);

            gamma = nd1/(S*v*sqt);
            vega = S*sqt*nd1;
            theta = -(S*v*nd1)/(2*sqt) - r*X*ert*Nd2;
            rho = X*t*ert*Nd2;

            return ( S*delta-X*ert *Nd2 > 0) * ( S*delta-X*ert *Nd2) ;

            }

        var data = source.get('data');
        var f_k = slider_k_call.get('value')
        var f_r = slider_r_call.get('value')
        var f_sigma = slider_sigma_call.get('value')
        var f_t = slider_t_call.get('value')
        x = data['x']
        y = data['y']

        for (i = 0; i < x.length; i++) {
            // black_scholes(call,S,X,r,v,t)
            y[i] = black_scholes(1,x[i],f_k,f_r,f_sigma,f_t)
        }
        source.trigger('change');
        """)


    slider_k_call = Slider(start=0.1, end=1.9, value=1, step=.1, title="strike", callback=callbackCall)
    slider_r_call = Slider(start=0, end=0.99, value=0.05, step=.01, title="risk-free rate", callback=callbackCall)
    slider_sigma_call = Slider(start=0, end=0.99, value=0.20, step=.01, title="volatility", callback=callbackCall)
    slider_t_call = Slider(start=0.05, end=20, value=1, step=.05, title="time", callback=callbackCall)

    callbackCall.args['slider_k_call'] = slider_k_call
    callbackCall.args['slider_t_call'] = slider_t_call
    callbackCall.args['slider_sigma_call'] = slider_sigma_call
    callbackCall.args['slider_r_call'] = slider_r_call

    script_call, div_call = components({"p":plot, "slider_k_call":WidgetBox(slider_k_call), "slider_r_call":WidgetBox(slider_r_call),
                              "slider_sigma_call":WidgetBox(slider_sigma_call),"slider_t_call":WidgetBox(slider_t_call)})

    x_put = [x/100 for x in range(1, 200)]
    y_put = [blsprice(1,X,0.05,0.20,1,0,"put") for X in x_put]
    sourcePut = ColumnDataSource(data=dict(x=x_put, y=y_put))

    plot_put = Figure(plot_width=400, plot_height=400)
    plot_put.line('x', 'y', source=sourcePut, line_width=3, line_alpha=0.6)

    # JavaScript:
    # No tools to calculate probability function and black-scholes
    # Calculate manually with approximation function: Not accurate result
    callbackPut = CustomJS(args=dict(source=sourcePut), code="""
        function ndist(z) {
            return (1.0/(Math.sqrt(2*Math.PI)))*Math.exp(-0.5*z);
        }

        function N(z) {
            b1 =  0.31938153;
            b2 = -0.356563782;
            b3 =  1.781477937;
            b4 = -1.821255978;
            b5 =  1.330274429;
            p  =  0.2316419;
            c2 =  0.3989423;
            a=Math.abs(z);
            if (a>6.0) {return 1.0;} // the probability is near 1
            if (a<-6.0){return 0.0;} // the probability is near 0
            t = 1.0/(1.0+a*p);
            b = c2*Math.exp((-z)*(z/2.0));
            n = ((((b5*t+b4)*t+b3)*t+b2)*t+b1)*t;
            n = 1.0-b*n;
            if (z < 0.0) {n = 1.0 - n;}
            return n;
        }

        function black_scholes(call,S,X,r,v,t) {
            // call = Boolean (to calc call, call=True, put: call=false)
            // S = stock prics, X = strike price, r = no-risk interest rate
            // v = volitility (1 std dev of S for (1 yr? 1 month?, you pick)
            // t = time to maturity

            // define some temp vars, to minimize function calls
            var sqt = Math.sqrt(t);
            var Nd2;  //N(d2), used often
            var nd1;  //n(d1), also used often
            var ert;  //e(-rt), ditto
            var delta;  //The delta of the option
            var price; //price of option

            d1 = (Math.log(S/X) + r*t)/(v*sqt) + 0.5*(v*sqt);
            d2 = d1 - (v*sqt);

            if (call) {
                delta = N(d1);
                Nd2 = N(d2);
            } else { //put
                delta = -N(-d1);
                Nd2 = -N(-d2);
            }

            ert = Math.exp(-r*t);
            nd1 = ndist(d1);

            gamma = nd1/(S*v*sqt);
            vega = S*sqt*nd1;
            theta = -(S*v*nd1)/(2*sqt) - r*X*ert*Nd2;
            rho = X*t*ert*Nd2;

            return ( S*delta-X*ert *Nd2 > 0) * ( S*delta-X*ert *Nd2) ;

            }

        var data = source.get('data');
        var f_k = slider_k_put.get('value')
        var f_r = slider_r_put.get('value')
        var f_sigma = slider_sigma_put.get('value')
        var f_t = slider_t_put.get('value')
        x = data['x']
        y = data['y']

        for (i = 0; i < x.length; i++) {
            // black_scholes(put,S,X,r,v,t)
            y[i] = black_scholes(0,x[i],f_k,f_r,f_sigma,f_t)
        }
        source.trigger('change');
        """)


    slider_k_put = Slider(start=0.1, end=1.9, value=1, step=.1, title="strike", callback=callbackPut)
    slider_r_put = Slider(start=0.01, end=0.40, value=0.05, step=.01, title="risk-free rate", callback=callbackPut)
    slider_sigma_put = Slider(start=0.01, end=0.99, value=0.20, step=.01, title="volatility", callback=callbackPut)
    slider_t_put = Slider(start=0.05, end=20, value=1, step=.05, title="time", callback=callbackPut)

    callbackPut.args['slider_k_put'] = slider_k_put
    callbackPut.args['slider_t_put'] = slider_t_put
    callbackPut.args['slider_sigma_put'] = slider_sigma_put
    callbackPut.args['slider_r_put'] = slider_r_put

    #script output for graph and sliders of call option
    script_call, div_call = components({"p_call":plot,
                            "slider_k_call":WidgetBox(slider_k_call), "slider_r_call":WidgetBox(slider_r_call),
                            "slider_sigma_call":WidgetBox(slider_sigma_call),"slider_t_call":WidgetBox(slider_t_call)})

    #script output for graph and sliders of put option
    script_put, div_put =components({"p_put":plot_put, #for put option
                            "slider_k_put":WidgetBox(slider_k_put), "slider_r_put":WidgetBox(slider_r_put),
                            "slider_sigma_put":WidgetBox(slider_sigma_put),"slider_t_put":WidgetBox(slider_t_put)})

    return render_template("bsm_graph.html", div_call = div_call, script_call = script_call, div_put=div_put, script_put=script_put)

# Bootstrapping with Swap Rates Page
# template file (first run or wrong input) : bootstr_upload.html
# template file (successful run with input) : bootstrap.html

@app.route('/bootstrap_upload/', methods=['GET', 'POST'])
def bootstrap_upload():

    if request.method == 'POST':
        target = os.path.join(APP_ROOT, 'text/')
        print(target)

        if not os.path.isdir(target):
            os.mkdir(target)


        #get the file, bootstrap and return the result to users
        #hasn't fixed the case that the file contains non-equally-sized columns

        for file in request.files.getlist("file"):

            filename = str(time.time()) + file.filename
            destination = "/".join([target, filename])
            file.save(destination)
            f = open(APP_ROOT+"\\text\\"+filename, "r")
            k = bootstrapping_col(text2data_col(f))
            result_col1 = k[0]
            result_col2 = k[1]
            range_result = range(len(result_col1))
            f.close()
            os.remove(APP_ROOT+"\\text\\"+filename)

        '''plot by bokeh'''
        p = figure(title='Spot Curve by Bokeh', plot_width=500, plot_height=400)
        # add the line
        p.line(result_col1, result_col2)
        # add axis labels
        p.xaxis.axis_label = "time to maturity"
        p.yaxis.axis_label = "spot rates"
        # create the HTML elements
        figJS, figDiv = components(p, CDN)

        return render_template('bootstrap.html', figJS = figJS, figDiv = figDiv, range_result = range_result,
                    result_col1=result_col1, result_col2=result_col2)
    else:
        return render_template('bootstr_upload.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
