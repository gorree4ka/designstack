<?php
/**
 * Title: Поля формы: текст, комментарий, почта, флажок
 * Slug: designstack/form-field
 * Categories: designstack
 * Inserter: no
 *
 * Обязательны только адрес и согласие, остальные поля помечены словом «необязательно» (D46). Ошибка стоит под полем,
 * связана с ним через aria-describedby и показана иконкой, а не одним цветом.
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<div class="ds-fields">
	<div class="ds-field">
		<label class="ds-field__label" for="ds-field-url">Адрес ресурса</label>
		<input class="ds-field__control" id="ds-field-url" type="url" name="resource_url" placeholder="https://">
	</div>
	<div class="ds-field">
		<label class="ds-field__label" for="ds-field-name">Название<span class="ds-field__optional">необязательно</span></label>
		<input class="ds-field__control" id="ds-field-name" type="text" name="resource_name" value="Excalidraw">
	</div>
	<div class="ds-field ds-field--textarea">
		<label class="ds-field__label" for="ds-field-comment">Комментарий<span class="ds-field__optional">необязательно</span></label>
		<textarea class="ds-field__control" id="ds-field-comment" name="resource_comment" rows="5" aria-describedby="ds-field-comment-hint"></textarea>
		<p class="ds-field__hint" id="ds-field-comment-hint">Чем ресурс полезен и кому подойдёт</p>
	</div>
	<div class="ds-field is-error">
		<label class="ds-field__label" for="ds-field-url-error">Адрес ресурса</label>
		<input class="ds-field__control" id="ds-field-url-error" type="url" name="resource_url_error" value="excalidraw com" aria-invalid="true" aria-describedby="ds-field-url-error-message">
		<p class="ds-field__error" id="ds-field-url-error-message"><?php echo designstack_icon( 'circle-x' ); ?>Это не похоже на адрес сайта. Проверьте, нет ли пробела или опечатки, например: https://excalidraw.com</p>
	</div>
	<div class="ds-field ds-field--checkbox">
		<input type="checkbox" id="ds-field-consent" name="resource_consent">
		<label class="ds-field__label" for="ds-field-consent">Соглашаюсь с <a class="ds-link" href="/privacy/">политикой данных</a></label>
	</div>
</div>
<!-- /wp:html -->
