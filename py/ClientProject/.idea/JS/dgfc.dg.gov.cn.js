var page = require('webpage').create();
page.viewportSize = { width: 1366, height: 600 };
var url='http://dgfc.dg.gov.cn/dgwebsite_v2/Vendition/ProjectInfo.aspx?townCode=1&projectName=&projectAddress=&companyName=&vc=97e68f5d'
page.open(url, function() {
    ret=page.evaluate(function() {
            $("#townName")[0].selectedIndex=1;
            $(".button").click();
        });
    setTimeout('print_cookies()',10000)
});

function print_cookies(){
    console.info(JSON.stringify(page.cookies, undefined, 4))
    phantom.exit()
}