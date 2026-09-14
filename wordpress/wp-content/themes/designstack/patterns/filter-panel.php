<?php
/**
 * Title: Панель фильтров раздела
 * Slug: designstack/filter-panel
 * Categories: designstack
 * Inserter: no
 *
 * Эталон блока «фильтры архива» этапа 12. От 900 — колонка слева, до 900 — панель снизу; значение без ресурсов
 * не показывается, поэтому недоступных флажков нет (US-14). Флажок и подпись обёрнуты в label: id не нужен.
 *
 * @package designstack
 */

$ds_groups = array(
	'Тема'          => array( 'UX-исследования', 'Прототипирование', 'UI и визуал', 'Типографика', 'Иконки и иллюстрации', 'Дизайн-системы', 'AI для дизайнера', 'Аналитика и метрики', 'Карьера и портфолио', 'Доступность', 'Мобильный дизайн', 'Веб и лендинги' ),
	'Цена'          => array( 'Бесплатно', 'Есть бесплатный тариф', 'Платно', 'Пробный период' ),
	'Доступ из РФ'  => array( 'Открывается из РФ', 'Открывается с перебоями', 'Недоступен из РФ' ),
	'Оплата из РФ'  => array( 'Оплачивается из РФ', 'Через посредника', 'Не оплатить из РФ', 'Российский' ),
	'Платформа'     => array( 'Веб', 'macOS', 'Windows', 'iOS', 'Android', 'Плагин Figma' ),
	'Грейд'         => array( 'Junior', 'Middle', 'Senior' ),
);

?>
<!-- wp:html -->
<form class="ds-filters ds-filters--sidebar" method="get" action="/tools/" aria-label="Фильтры">
	<?php foreach ( $ds_groups as $ds_legend => $ds_options ) : ?>
	<fieldset class="ds-filters__group">
		<legend class="ds-filters__legend"><?php echo esc_html( $ds_legend ); ?></legend>
		<?php foreach ( $ds_options as $ds_index => $ds_option ) : ?>
		<label class="ds-filters__option"><input type="checkbox"<?php echo 1 === $ds_index && 'Тема' === $ds_legend ? ' checked' : ''; ?>><?php echo esc_html( $ds_option ); ?></label>
		<?php endforeach; ?>
	</fieldset>
	<?php endforeach; ?>
	<div class="ds-filters__actions">
		<button type="submit" class="ds-button ds-button--primary">Применить</button>
		<a class="ds-link ds-chips__reset" href="/tools/">Сбросить фильтры</a>
	</div>
</form>
<!-- /wp:html -->
