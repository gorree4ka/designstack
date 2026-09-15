<?php
/**
 * Title: Уведомления: состояние записи и сообщения формы
 * Slug: designstack/notice
 * Categories: designstack
 * Inserter: no
 *
 * Тонированный фон — только у состояния записи (D50). Сообщения формы нейтральные: подложка bg-info с рамкой
 * («Край поверхности», foundation.md). Тексты — docs/VOICE.md.
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<div class="ds-stack">
	<div class="ds-notice ds-notice--dead"><?php echo designstack_icon( 'circle-x' ); ?><div class="ds-notice__body"><p class="ds-notice__title">Закрыт</p><p class="ds-notice__text">Ресурс больше не работает. Запись оставляем ради истории и ссылки на аналог.</p><a class="ds-button ds-button--primary" href="#analogs">Показать аналог</a></div></div>
	<div class="ds-notice ds-notice--changed"><?php echo designstack_icon( 'triangle-alert' ); ?><div class="ds-notice__body"><p class="ds-notice__title">Условия изменились</p><p class="ds-notice__text">С прошлой проверки поменялись цена, тариф или доступ. Что именно — написано ниже в оценке.</p></div></div>
	<div class="ds-notice ds-notice--stale"><?php echo designstack_icon( 'clock' ); ?><div class="ds-notice__body"><p class="ds-notice__title">Давно не проверяли</p><p class="ds-notice__text">Проверено больше 90 дней назад. Скоро посмотрим заново: условия могли измениться.</p></div></div>
	<div class="ds-notice ds-notice--info"><?php echo designstack_icon( 'info' ); ?><div class="ds-notice__body"><p class="ds-notice__text">Не получилось отправить: сервер не ответил. Введённое осталось в форме — отправь ещё раз через минуту.</p></div></div>
	<div class="ds-notice ds-notice--info"><?php echo designstack_icon( 'info' ); ?><div class="ds-notice__body"><p class="ds-notice__text">С этого подключения за час уже пришло три предложения. Попробуйте ещё раз через час — так сайт защищается от спама.</p></div></div>
	<div class="ds-notice ds-notice--info"><?php echo designstack_icon( 'info' ); ?><div class="ds-notice__body"><p class="ds-notice__text"><a class="ds-link" href="/resource/penpot/">Penpot</a> уже есть в каталоге</p></div></div>
</div>
<!-- /wp:html -->
