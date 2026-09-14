<?php
/**
 * Title: Факты ресурса
 * Slug: designstack/resource-facts
 * Categories: designstack
 * Inserter: no
 *
 * Пары «подпись — значение» (US-28): пустое необязательное поле не выводится, поля чужого типа не показываются.
 * В узкой колонке подпись встаёт над значением — это контейнерный запрос, а не ширина окна.
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<aside class="ds-facts" aria-label="Факты о ресурсе">
	<dl class="ds-facts__list">
		<dt class="ds-facts__label">Цена</dt>
		<dd class="ds-facts__value">Есть бесплатный тариф<span class="ds-facts__note">бесплатно для студентов и преподавателей</span></dd>
		<dt class="ds-facts__label">Доступ из РФ</dt>
		<dd class="ds-facts__value"><span class="ds-badge ds-badge--success"><?php echo designstack_icon( 'circle-check' ); ?>Открывается из РФ</span><span class="ds-facts__note">Сайт открывается из России напрямую.</span></dd>
		<dt class="ds-facts__label">Оплата из РФ</dt>
		<dd class="ds-facts__value"><span class="ds-badge ds-badge--error"><?php echo designstack_icon( 'circle-x' ); ?>Не оплатить из РФ</span><span class="ds-facts__note">Российской картой не оплатить: нужен зарубежный счёт.</span></dd>
		<dt class="ds-facts__label">Язык</dt>
		<dd class="ds-facts__value">На английском</dd>
		<dt class="ds-facts__label">Грейд</dt>
		<dd class="ds-facts__value">Junior · Middle</dd>
		<dt class="ds-facts__label">Темы</dt>
		<dd class="ds-facts__value"><a class="ds-link" href="/topic/prototyping/">Прототипирование</a> · <a class="ds-link" href="/topic/ui-visual/">UI и визуал</a></dd>
		<dt class="ds-facts__label">Платформы</dt>
		<dd class="ds-facts__value">Веб · macOS · Windows</dd>
		<dt class="ds-facts__label">Бесплатный тариф</dt>
		<dd class="ds-facts__value">есть</dd>
		<dt class="ds-facts__label">ИИ-функции</dt>
		<dd class="ds-facts__value">есть</dd>
	</dl>
</aside>
<!-- /wp:html -->
