<?php
/**
 * Title: Карточка ресурса
 * Slug: designstack/resource-card
 * Categories: designstack
 * Inserter: no
 *
 * Одна карточка на все списки (US-26). Порядок частей — D50: логотип, название, подпись типа, состояние записи,
 * вердикт, метки, теги, нижняя строка с датой и контурной кнопкой. Клик по карточке ведёт на страницу ресурса (D16),
 * поэтому ссылка названия растянута на карточку, а кнопка лежит выше неё. Эталон для render.php этапа 12.
 *
 * @package designstack
 */

$ds_cards = array(
	array(
		'name'    => 'Figma',
		'type'    => 'Инструмент',
		'kind'    => 'tool',
		'state'   => null,
		'verdict' => 'Стандарт для интерфейсов, но платный тариф российской картой не оплатить',
		'badges'  => array( array( '', '', 'Есть бесплатный тариф' ), array( 'success', 'circle-check', 'Открывается из РФ' ), array( 'error', 'circle-x', 'Не оплатить из РФ' ) ),
		'tags'    => 'прототипы · командная работа',
		'date'    => 'Проверено 3&nbsp;сен 2026',
		'action'  => 'site',
	),
	array(
		'name'    => 'Figma Learn: прототипирование',
		'type'    => 'Учебный материал',
		'kind'    => 'learning',
		'state'   => null,
		'verdict' => 'Официальные уроки по связям, переходам и умной анимации в Figma',
		'badges'  => array( array( '', '', 'Бесплатно' ), array( 'success', 'circle-check', 'Открывается из РФ' ) ),
		'tags'    => 'прототипы · видео',
		'date'    => 'Проверено 4&nbsp;сен 2026',
		'action'  => 'site',
	),
	array(
		'name'    => 'Untitled UI',
		'type'    => 'Ассет',
		'kind'    => 'asset',
		'state'   => null,
		'verdict' => 'Большой UI-кит: хватит, чтобы собрать прототип без своих компонентов',
		'badges'  => array( array( '', '', 'Есть бесплатный тариф' ), array( 'success', 'circle-check', 'Открывается из РФ' ), array( 'error', 'circle-x', 'Не оплатить из РФ' ) ),
		'tags'    => 'UI-кит · Figma',
		'date'    => 'Проверено 29&nbsp;авг 2026',
		'action'  => 'site',
	),
	array(
		'name'    => 'UX Horn',
		'type'    => 'Сообщество',
		'kind'    => 'community',
		'state'   => null,
		'verdict' => 'Конспекты статей по UX тезисами, около трёх постов в неделю',
		'badges'  => array( array( '', '', 'Бесплатно' ), array( 'success', 'circle-check', 'Открывается из РФ' ) ),
		'tags'    => 'Telegram · вакансии',
		'date'    => 'Проверено 5&nbsp;сен 2026',
		'action'  => 'site',
	),
	array(
		'name'    => 'Framer',
		'type'    => 'Инструмент',
		'kind'    => 'tool',
		'state'   => array( 'tint-warning', 'triangle-alert', 'Условия изменились' ),
		'verdict' => 'Собирает сайт прямо из макета; бесплатный план после смены тарифов урезан',
		'badges'  => array( array( '', '', 'Есть бесплатный тариф' ), array( 'warning', 'triangle-alert', 'Открывается с перебоями' ), array( 'error', 'circle-x', 'Не оплатить из РФ' ) ),
		'tags'    => 'сайты · анимация',
		'date'    => 'Проверено 3&nbsp;сен 2026',
		'action'  => 'site',
	),
	array(
		'name'    => 'NN/g: бумажные прототипы',
		'type'    => 'Учебный материал',
		'kind'    => 'learning',
		'state'   => array( 'tint-warning', 'clock', 'Давно не проверяли' ),
		'verdict' => 'Как проверить идею на бумаге за час до первого макета',
		'badges'  => array( array( '', '', 'Бесплатно' ), array( 'success', 'circle-check', 'Открывается из РФ' ) ),
		'tags'    => 'исследования · статья',
		'date'    => 'Проверено 5&nbsp;июн 2026',
		'action'  => 'site',
	),
	array(
		'name'    => 'InVision',
		'type'    => 'Инструмент',
		'kind'    => 'tool',
		'state'   => array( 'tint-error', 'circle-x', 'Закрыт' ),
		'verdict' => 'Сервис закрыт в конце 2024 года, прототипы переносят в Figma или Penpot',
		'badges'  => array( array( '', '', 'Платно' ), array( 'error', 'circle-x', 'Недоступен из РФ' ), array( 'error', 'circle-x', 'Не оплатить из РФ' ) ),
		'tags'    => 'прототипы',
		'date'    => 'Проверено 1&nbsp;сен 2026',
		'action'  => 'analog',
	),
	array(
		'name'    => 'Google Jamboard',
		'type'    => 'Инструмент',
		'kind'    => 'tool',
		'state'   => array( 'tint-error', 'circle-x', 'Закрыт' ),
		'verdict' => 'Доска для группировки заметок после интервью; закрыта в конце 2024 года',
		'badges'  => array( array( '', '', 'Бесплатно' ), array( 'success', 'circle-check', 'Открывается из РФ' ) ),
		'tags'    => 'доска · заметки',
		'date'    => 'Проверено 2&nbsp;сен 2026',
		'action'  => 'none',
	),
);

?>
<!-- wp:html -->
<?php foreach ( $ds_cards as $ds_card ) : ?>
<article class="ds-card ds-card--<?php echo esc_attr( $ds_card['kind'] ); ?>">
	<div class="ds-card__head">
		<span class="ds-logo" aria-hidden="true"><?php echo esc_html( mb_strtoupper( mb_substr( $ds_card['name'], 0, 1 ) ) ); ?></span>
		<div class="ds-card__titles">
			<h3 class="ds-card__title"><a class="ds-card__link" href="/resource/figma/"><?php echo esc_html( $ds_card['name'] ); ?></a></h3>
			<span class="ds-card__type"><?php echo esc_html( $ds_card['type'] ); ?></span>
		</div>
	</div>
	<?php if ( ! empty( $ds_card['state'] ) ) : ?>
	<span class="ds-badge ds-badge--<?php echo esc_attr( $ds_card['state'][0] ); ?> ds-card__state"><?php echo designstack_icon( $ds_card['state'][1] ); ?><?php echo esc_html( $ds_card['state'][2] ); ?></span>
	<?php endif; ?>
	<p class="ds-card__verdict"><?php echo esc_html( $ds_card['verdict'] ); ?></p>
	<div class="ds-badges">
		<?php foreach ( $ds_card['badges'] as $ds_badge ) : ?>
		<span class="ds-badge<?php echo $ds_badge[0] ? ' ds-badge--' . esc_attr( $ds_badge[0] ) : ''; ?>"><?php echo $ds_badge[1] ? designstack_icon( $ds_badge[1] ) : ''; ?><?php echo esc_html( $ds_badge[2] ); ?></span>
		<?php endforeach; ?>
	</div>
	<p class="ds-card__tags"><?php echo esc_html( $ds_card['tags'] ); ?></p>
	<div class="ds-card__foot">
		<p class="ds-meta ds-meta--xs ds-card__date"><?php echo wp_kses_post( $ds_card['date'] ); ?></p>
		<?php if ( 'site' === $ds_card['action'] ) : ?>
		<span class="ds-card__action"><a class="ds-button ds-button--secondary ds-button--sm" href="https://www.figma.com/" target="_blank" rel="noopener">Перейти на сайт<span class="screen-reader-text">откроется в новой вкладке</span></a></span>
		<?php elseif ( 'analog' === $ds_card['action'] ) : ?>
		<span class="ds-card__action"><a class="ds-button ds-button--secondary ds-button--sm" href="/resource/figma/#analogs">Показать аналог</a></span>
		<?php endif; ?>
	</div>
</article>
<?php endforeach; ?>
<!-- /wp:html -->
