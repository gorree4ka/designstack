<?php
/**
 * Title: Форма «Предложить ресурс»
 * Slug: designstack/suggest-form
 * Categories: designstack
 * Inserter: no
 *
 * Эталон блока формы этапа 12 (US-42, D46): обязательны адрес и согласие, ловушка вне экрана и вне фокуса,
 * при отправке кнопка не бледнеет, а меняет подпись и получает aria-busy.
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<form class="ds-suggest-form" method="post" action="/suggest/thanks/">
	<div class="ds-field">
		<label class="ds-field__label" for="ds-suggest-url">Адрес ресурса</label>
		<input class="ds-field__control" id="ds-suggest-url" type="url" name="resource_url" placeholder="https://" required>
	</div>
	<div class="ds-field">
		<label class="ds-field__label" for="ds-suggest-name">Название<span class="ds-field__optional">необязательно</span></label>
		<input class="ds-field__control" id="ds-suggest-name" type="text" name="resource_name">
	</div>
	<div class="ds-field ds-field--textarea">
		<label class="ds-field__label" for="ds-suggest-comment">Комментарий<span class="ds-field__optional">необязательно</span></label>
		<textarea class="ds-field__control" id="ds-suggest-comment" name="resource_comment" rows="5" maxlength="1000" aria-describedby="ds-suggest-comment-hint"></textarea>
		<p class="ds-field__hint" id="ds-suggest-comment-hint">Чем ресурс полезен и кому подойдёт</p>
	</div>
	<div class="ds-field">
		<label class="ds-field__label" for="ds-suggest-email">Почта<span class="ds-field__optional">необязательно</span></label>
		<input class="ds-field__control" id="ds-suggest-email" type="email" name="resource_email" aria-describedby="ds-suggest-email-hint">
		<p class="ds-field__hint" id="ds-suggest-email-hint">Напишем, взяли ресурс в каталог или нет</p>
	</div>
	<div class="ds-field ds-field--checkbox">
		<input type="checkbox" id="ds-suggest-consent" name="resource_consent" required>
		<label class="ds-field__label" for="ds-suggest-consent">Соглашаюсь с <a class="ds-link" href="/privacy/">политикой данных</a></label>
	</div>
	<div class="ds-suggest-form__trap" aria-hidden="true"><label>Не заполняй это поле<input type="text" name="resource_site" tabindex="-1" autocomplete="off"></label></div>
	<button type="submit" class="ds-button ds-button--primary ds-button--lg ds-suggest-form__submit">Предложить ресурс</button>
</form>
<!-- /wp:html -->
