<?php
/**
 * Title: Метки: цена, грейд, доступ, оплата, состояние записи
 * Slug: designstack/badge
 * Categories: designstack
 * Inserter: no
 *
 * Эталон разметки для этапа 12. Статус — иконка и слово, цвет третий канал; тонированный фон только у состояния
 * записи и давности проверки (D50, docs/ds/foundation.md).
 *
 * @package designstack
 */

?>
<!-- wp:html -->
<div class="ds-badges">
	<span class="ds-badge">Бесплатно</span>
	<span class="ds-badge">Есть бесплатный тариф</span>
	<span class="ds-badge">Платно</span>
	<span class="ds-badge">Пробный период</span>
	<span class="ds-badge">Junior</span>
	<span class="ds-badge ds-badge--success"><?php echo designstack_icon( 'circle-check' ); ?>Открывается из РФ</span>
	<span class="ds-badge ds-badge--error"><?php echo designstack_icon( 'circle-x' ); ?>Недоступен из РФ</span>
	<span class="ds-badge ds-badge--success"><?php echo designstack_icon( 'circle-check' ); ?>Оплачивается из РФ</span>
	<span class="ds-badge ds-badge--warning"><?php echo designstack_icon( 'triangle-alert' ); ?>Через посредника</span>
	<span class="ds-badge ds-badge--success"><?php echo designstack_icon( 'circle-check' ); ?>Российский</span>
	<span class="ds-badge ds-badge--error"><?php echo designstack_icon( 'circle-x' ); ?>Не оплатить из РФ</span>
	<span class="ds-badge ds-badge--tint-warning"><?php echo designstack_icon( 'triangle-alert' ); ?>Условия изменились</span>
	<span class="ds-badge ds-badge--tint-error"><?php echo designstack_icon( 'circle-x' ); ?>Закрыт</span>
	<span class="ds-badge ds-badge--tint-warning"><?php echo designstack_icon( 'clock' ); ?>Давно не проверяли</span>
</div>
<!-- /wp:html -->
