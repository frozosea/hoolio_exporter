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

        await agent.goto('https://ss.ge/ru/недвижимость');
        await agent.waitForState({
            name: 'dlfLoaded',
            all(assert) {
                assert(agent.isPaintingStable);
            },
        });
        await agent.waitForLoad('DomContentLoaded', {timeoutMs: 600000});

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


        await agent.goto('https://ss.ge/ru/недвижимость/create?DeleteDraft=True');
        await agent.waitForState({
            name: 'dlfLoaded',
            all(assert) {
                assert(agent.isPaintingStable);
            },
        });
        await agent.waitForLoad('DomContentLoaded', {timeoutMs: 600000});
        await waitSelector('#create-edit-realestate-form > div.center-content > div.category-section > div.section-row.ss-categories > div > a.category-list-item.realestate-category-list-item.active').$click();
        await waitSelector('%s').$click(); //property type
        await waitSelector('%s').$click(); //transaction type
        await waitSelector('#create-edit-realestate-form > div.center-content > div.create-edit-inputs-container > div.section-row.create-edit-location > div:nth-child(2) > div > div > button').$click();
        await waitSelector('#bs-select-1');
        await waitSelector('%s').$click(); //city button
        await sleep(1000); //wait until city menu hidden
        await waitSelector('#street-select').$clearInput();
        await waitSelector('#street-select').$type('%s'); //street
        await waitSelector('#create-edit-realestate-form > div.center-content > div.create-edit-inputs-container > div.section-row.create-edit-location > div.d-flex.street-select-form > div:nth-child(1) > div.searched-stree-list > ul > li:nth-child(1) > ul > li').$click();
        await waitSelector('#StreetNumber').$clearInput();
        await waitSelector('#StreetNumber').$type('%s'); //house number
        await waitSelector(`#room-${%s}`).$click(); //rooms quantity
        await waitSelector('#bedroom1')
        await waitSelector(`#bedroom${%s}`).$click(); //bedrooms quantity
        await waitSelector('#TotalArea').$type('%s'); //area
        await waitSelector('#Floor').$clearInput();
        await waitSelector('#Floor').$type('%s'); // floor
        await waitSelector('#Floors').$clearInput();
        await waitSelector('#Floors').$type('%s'); // floors
        await waitSelector('%s').$click(); //balcony
        await waitSelector('%s').$click(); //toilet
        await waitSelector('%s').$click(); //building type
        await waitSelector('#checkbox-428').$click();
        await waitSelector('%s').$click(); //property condition

        let heating = %s;
        if (heating) {
            await waitSelector('#create-edit-realestate-form > div.center-content > div.create-edit-inputs-container > div.create-edit-dynamic-fileds > div.section-row.application-main-info > div > div > div:nth-child(4)').$click()
        }

        let hasGas = %s;
        if (hasGas) {
            await waitSelector('#create-edit-realestate-form > div.center-content > div.create-edit-inputs-container > div.create-edit-dynamic-fileds > div.section-row.application-main-info > div > div > div:nth-child(8)').$click();
        }

        await waitSelector('#DescriptionGe').$clearInput();
        await waitSelector('#DescriptionGe').$type('%s'); //ge description
        await waitSelector('#translate_to_en').$clearInput();
        await waitSelector('#translate_to_en').$type('%s'); //en description
        await waitSelector('#translate_to_ru').$clearInput();
        await waitSelector('#translate_to_ru').$type('%s'); //ru description
        await waitSelector('#imageFile').$click();
        const fileChooser = await agent.waitForFileChooser();
        await fileChooser.chooseFiles(%s);
        await waitSelector('#imageGallery');
        await waitSelector('#PriceUsd').$clearInput();
        await waitSelector('#PriceUsd').$type('%s'); //usd price
        await waitSelector('#create-edit-realestate-form > div.center-content > div.create-edit-inputs-container > div.section-row.contact-section.numbers-search > div.form-group.add-phone-number > div > div.phone-number-list > div.phone-number-socials > label:nth-child(1)').$click();//accept whatsapp
        await waitSelector('#create-edit-realestate-form > div.center-content > div.create-edit-inputs-container > div.section-row.contact-section.numbers-search > div.form-group.add-phone-number > div > div.phone-number-list > div.phone-number-socials > label:nth-child(2)').$click();//accept viber
        await waitSelector('#create-edit-realestate-form > div.create-first-page > button.create-edit-btn.next-btn.valid').$click();
        await waitSelector('#create-edit-realestate-form > div.create-application-row > div.create-edit-app-buttons > button.create-edit-btn.create-application-btn').$click();
        await waitSelector('#CreateArticleConfirmation > div > div')
}
)();