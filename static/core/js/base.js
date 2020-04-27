function update_dashboard(){
    var event_status = $('#filtering').find(":selected").text();
    var event_name = $("#search").find('input').val()
    $.ajax({
        url: 'filtered_event_summary',
        data: {'event_status':event_status, "event_name":event_name},
        dataType: 'json',
        success: function(data){
            $('#rank_table tbody').empty();
            var html = '';
            for (var each in data['event_which_has_subscribers']) {
            html += '<tr><th>' + data['event_which_has_subscribers'][each]['name'] +
                    '</th><td>' + data['event_which_has_subscribers'][each]['total_tickets'] +
                    '</td><td>' + data['event_which_has_subscribers'][each]['total_sold_tickets'] +
                    '</td><td>' + data['event_which_has_subscribers'][each]['final_amount'] +
                    '</td><td>' + data['event_which_has_subscribers'][each]['status'] +
                    '</td><td>' + data['event_which_has_subscribers'][each]['event_created_by'] + '</td></tr>';
            }
            for (var each in data['events_not_subscribed']) {
            html += '<tr><th>' + data['events_not_subscribed'][each]['name'] +
                    '</th><td>' + data['events_not_subscribed'][each]['no_of_tickets'] +
                    '</td><td>' + data['events_not_subscribed'][each]['sold_tickets'] +
                    '</td><td>' + data['events_not_subscribed'][each]['sold_tickets'] +
                    '</td><td>' + data['events_not_subscribed'][each]['status'] +
                    '</td><td>' + data['events_not_subscribed'][each]['event_created_by'] + '</td></tr>';
            }
            $('#rank_table tbody').append(html)
            $('#rank_table tbody tr:odd').addClass('grp-row grp-row-odd');
            $('#rank_table tbody tr:even').addClass('grp-row grp-row-even');
            $('#rank_table tr').attr('scope','row')
            $('#rank_table tr td:first-child').css('text-align','center');
            $('#count').val(data['total_count']+" total").html(data['total_count']+" total")
            $('#count1').val(data['total_count']+" total").html(data['total_count']+" total")
            $('#revenue').val(data['total_revenue']).html(data['total_revenue'])
            $('#revenue').addClass('text-color')
            $("a.grp-pulldown-handler").closest(".grp-pulldown-container").removeClass('grp-pulldown-state-open').children(".grp-pulldown-content").removeClass('disp1');
            $("a.grp-pulldown-handler").closest(".grp-pulldown-container").children(".grp-pulldown-content").addClass('disp');
            var data2 = data['data2'];
            var max_length = data['max_length'];
            var completed = data['completed'];
            var ongoing = data['ongoing'];
            var cancelled = data['cancelled'];
            var event_organisers = data['event_organisers'];
            var data = data['data'];
            $('#piechart').remove();
            $('#lineChart').remove();
            $('#mixchart').remove();
            $('#chartAxis').remove();
            $('#chart').append('<canvas id="piechart"></canvas>');
            $('#chartArea').append('<canvas id="lineChart" width="850" height="300"></canvas>');
            $('#chart2').append('<canvas id="mixchart" style="width:80%" height="300"></canvas>');
            $('#chartyaxis').append('<canvas id="chartAxis" height="300" width="20" style="background-color:white"></canvas>');
            var ctx = $("#piechart");
            var piechart = new Chart(ctx, {
                type: 'doughnut',
                data: data,
                options : {
                    legend: {
                           display: true,
                           position: 'left',
                    }
                }
            });
            var ctx = $("#mixchart");
            var mixedChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    datasets: [{
                        label: 'Completed',
                        data: completed,
                        type: 'line',
                        backgroundColor: 'rgba(255, 255, 255, 0)',
                        borderColor: 'rgba(0,255,127, 1)',
                        borderWidth: 1,
                    },
                     {
                        label: 'Ongoing',
                        data: ongoing,
                        type: 'line',
                        backgroundColor: 'rgba(255, 255, 255, 0)',
                        borderColor: 'rgba(255,140,0, 1)',
                        borderWidth: 1,
                    },
                     {
                        label: 'Cancelled',
                        data: cancelled,
                        type: 'line',
                        backgroundColor: 'rgba(255, 255, 255, 0)',
                        borderColor: 'rgba(255,0,0, 1)',
                        borderWidth: 1,
                    },
                    ],
                    labels: event_organisers
                },
                options: {
                    scales:
                    {
                        yAxes:
                        [{
                              scaleLabel:
                              {
                                    display: true,
                                    fontSize: 14,
                                    fontStyle: 'bold',
                                    labelString: 'Count of events'
                              }
                        }],
                        xAxes:
                        [{
                              scaleLabel:
                              {
                                    display: true,
                                    fontSize: 14,
                                    fontStyle: 'bold',
                                    labelString: 'Organisers'
                              }
                        }],
                    }
                }
            });

            var ctx = document.getElementById("lineChart").getContext('2d');
            var targetCtx = document.getElementById("chartAxis").getContext('2d');
            targetCtx.clearRect(0, 0, targetCtx.canvas.width, targetCtx.canvas.height);

            var lineChart = new Chart(ctx, {
                type: 'bar',
                data: data2,
                options: {
                    hover:{mode: null},
                    scales:{
                        xAxes:[
                            {
                                stacked: true,
                                id: "bar-x-axis1",
                                ticks: {
                                autoSkip: false,
                                maxRotation: 90,
                                minRotation: 90
                                }
                            },
                            {
                                display: false,
                                stacked: true,
                                id: "bar-x-axis2",
                                offset: true,
                                ticks: {
                                autoSkip: false,
                                maxRotation: 90,
                                minRotation: 90
                                }
                            },
                        ],
                        yAxes:[{
                            ticks:{
                                beginAtZero: true
                            },
                            stacked:false,
                            scaleLabel:
                            {
                                display: true,
                                fontSize: 14,
                                fontStyle: 'bold',
                                labelString: 'Total tickets vs Sold tickets'
                            },
                        }],
                    },
                    animation: {
                      onComplete: function() {
                        if (!this.rectangleSet) {
                          var scale = window.devicePixelRatio;
                          var copyWidth = lineChart.scales['y-axis-0'].width + 3;
                          var copyHeight = lineChart.scales['y-axis-0'].height + lineChart.scales['y-axis-0'].top + max_length;

                          targetCtx.scale(scale, scale);
                          targetCtx.canvas.width = copyWidth * scale;
                          targetCtx.canvas.height = copyHeight * scale;
                          targetCtx.canvas.style.width = copyWidth + 'px';
                          targetCtx.canvas.style.height = copyHeight + 'px';
                          targetCtx.drawImage(ctx.canvas, 0, 0, copyWidth * scale, copyHeight * scale, 0, 0,copyWidth * scale, copyHeight * scale);
                          ctx.clearRect(0, 0, copyWidth, copyHeight);
                          this.rectangleSet = true;
                        }
                      },
                      onProgress: function() {
                        if (this.rectangleSet) {
                          var copyWidth = lineChart.scales['y-axis-0'].width;
                          var copyHeight = lineChart.scales['y-axis-0'].height + lineChart.scales['y-axis-0'].top + 10;
                          ctx.clearRect(0, 0, copyWidth, copyHeight);
                        }
                      },
                    }
                }
            });
},
        error: function(data){
            console.log(data)
            alert('Some Problem occurred with updating dashboard');
        }
    });
}