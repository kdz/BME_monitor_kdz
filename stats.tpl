<!DOCTYPE html>

<!-- THIS TEMPLATE IS CALLED WITH 1 KEYWORD ARGUMENT: world -->

<html>
<head lang="en">

    <!-- use publicly available URLs for the FLOT JavaScript library (which uses the jQuery library) -->
    <script language="javascript" type="text/javascript" src="http://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
    <script language="javascript" type="text/javascript" src="http://cdnjs.cloudflare.com/ajax/libs/flot/0.8.3/jquery.flot.min.js"></script>

    <script type="text/javascript">
        // When the Document is ready i.e. all scripts, images, etc. loaded ...
        $(document).ready(
                // ... then run this function ...
                function() {
                    var body_h = {{world.body_hist[0:11]}};
                    var env_h = {{world.env_hist[0:11]}};
                    // TODO: pass all options as Python parameters, don't harcode in JavaScript
                    var s1 = {data: body_h, label: 'Body Temp'};
                    var s2 = {data: env_h, label: 'Env Temp'};
                    var options = {legend: {show: true},
                        series: {lines: {show: true}, points: {show: true}}
                    };
                    // TODO: add FAN-ON/OFF events as separate series with markers (no lines)
                    // Good customizations: http://goo.gl/e7riCQ   http://goo.gl/QPTHgc

                    // ... to insert the plot into <div id="graph"...>
                    $.plot("#graph", [s1, s2], options);
                })
        // TODO: poll for updates
    </script>

</head>
<body>

<h1>Your Baby Monitor</h1>

<h2>Graph</h2>
<div id="graph" style="width:600px;height:300px"></div>

<h2>Device Status</h2>
<ul>
    <li>Heater: {{"ON" if world.heater_is_on else "OFF"}}</li>
    <li>Fan: {{"ON" if world.fan_is_on else "OFF"}}</li>
</ul>


<h2>Device Controls</h2>
<ul>
    <li><a href='/heat_on'>Turn Heat On</a></li>
    <li><a href='/heat_off'>Turn Heat Off</a></li>
    <li><a href='/fan_on'>Turn Fan On</a></li>
    <li><a href='/fan_off'>Turn Fan Off</a></li>
</ul>


</body>
</html>