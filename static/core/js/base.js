function update_dashboard(){
    var event_status = $('#filtering').find(":selected").text();
    var event_name = $("#search").find('input').val()
    console.log(event_name)
    $.ajax({
        url: 'filtered_event_summary',
        data: {'event_status':event_status, "event_name":event_name},
        dataType: 'json',
        success: function(data){
            $('#rank_table tbody').empty();
            var html = '';
            console.log(data)
            for (var each in data['event_which_has_subscribers']) {
            html += '<tr><th>' + data['event_which_has_subscribers'][each]['name'] +
                    '</th><td>' + data['event_which_has_subscribers'][each]['total_tickets'] +
                    '</td><td>' + data['event_which_has_subscribers'][each]['total_sold_tickets'] +
                    '</td><td>' + data['event_which_has_subscribers'][each]['final_amount'] +
                    '</td><td>' + data['event_which_has_subscribers'][each]['status'] +  '</td></tr>';;
            }
            for (var each in data['events_not_subscribed']) {
            html += '<tr><th>' + data['events_not_subscribed'][each]['name'] +
                    '</th><td>' + data['events_not_subscribed'][each]['no_of_tickets'] +
                    '</td><td>' + data['events_not_subscribed'][each]['sold_tickets'] +
                    '</td><td>' + data['events_not_subscribed'][each]['sold_tickets'] +
                    '</td><td>' + data['events_not_subscribed'][each]['status'] +  '</td></tr>';
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
            $("a.grp-pulldown-handler").closest(".grp-pulldown-container").removeClass('grp-pulldown-state-open').children(".grp-pulldown-content").addClass('disp');
            var data = data['data'];
            $('#piechart').remove();
            $('.chart').append('<canvas id="piechart" width="500" height="200" ><canvas>');
            var ctx = $("#piechart");
            var piechart = new Chart(ctx, {
                type: 'pie',
                data: data,
            });
},
        error: function(data){
            console.log(data)
            alert('Some Problem occurred with updating dashboard');
        }
    });
}