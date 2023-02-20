(async () => {
        function sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        };

        async function waitSelector(selector) {
            let s = await agent.querySelector(selector);
            while (!s) {
                await sleep(1000);
                s = await agent.querySelector(selector);
            }
            ;
            return s
        };

        await agent.goto('https://ss.ge/ru/недвижимость',6000000000);
        await agent.waitForLoad('DomContentLoaded', {timeoutMs: 6000000000});

        await waitSelector('#header_block > div.topHeader > div > div > div.topHeaderRight > div.login_form > a').$click();
        await waitSelector('#LoginRegisterModal > div > div')
        await waitSelector('#UserName').$clearInput()
        await waitSelector('#UserName').$type('%s')
        await waitSelector('#Password').$clearInput()
        await waitSelector('#Password').$type("%s")
        await waitSelector('#login_button').$click();

        let loginButton = await waitSelector('#header_block > div.topHeader > div > div > div.topHeaderRight > div.dropdown.user-dropdown > button > p');
        await agent.waitForState({
            name: 'dlfLoaded',
            all(assert) {
                assert(loginButton.textContent.includes(email));
            },
        });
        const cookieStorage = await agent.activeTab.cookieStorage;
        for (cookie in cookieStorage){
            console.log(cookie);
        }

}
)();