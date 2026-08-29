// GENERATED CODE - DO NOT MODIFY BY HAND
// coverage:ignore-file
// ignore_for_file: type=lint, type=warning, deprecated_member_use, deprecated_member_use_from_same_package
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'lista_espera_entrada.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

// GENERATED CODE - DO NOT MODIFY BY HAND
// dart format off
T _$identity<T>(T value) => value;

/// @nodoc
mixin _$ListaEsperaEntrada {

 int get id; int get recursoId; String get fecha; String get horaInicio; String get horaFin; String get estado; String get createdAt;
/// Create a copy of ListaEsperaEntrada
/// with the given fields replaced by the non-null parameter values.
@JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
$ListaEsperaEntradaCopyWith<ListaEsperaEntrada> get copyWith => _$ListaEsperaEntradaCopyWithImpl<ListaEsperaEntrada>(this as ListaEsperaEntrada, _$identity);

  /// Serializes this ListaEsperaEntrada to a JSON map.
  Map<String, dynamic> toJson();


@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is ListaEsperaEntrada&&(identical(other.id, id) || other.id == id)&&(identical(other.recursoId, recursoId) || other.recursoId == recursoId)&&(identical(other.fecha, fecha) || other.fecha == fecha)&&(identical(other.horaInicio, horaInicio) || other.horaInicio == horaInicio)&&(identical(other.horaFin, horaFin) || other.horaFin == horaFin)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,recursoId,fecha,horaInicio,horaFin,estado,createdAt);

@override
String toString() {
  return 'ListaEsperaEntrada(id: $id, recursoId: $recursoId, fecha: $fecha, horaInicio: $horaInicio, horaFin: $horaFin, estado: $estado, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class $ListaEsperaEntradaCopyWith<$Res>  {
  factory $ListaEsperaEntradaCopyWith(ListaEsperaEntrada value, $Res Function(ListaEsperaEntrada) _then) = _$ListaEsperaEntradaCopyWithImpl;
@useResult
$Res call({
 int id, int recursoId, String fecha, String horaInicio, String horaFin, String estado, String createdAt
});




}
/// @nodoc
class _$ListaEsperaEntradaCopyWithImpl<$Res>
    implements $ListaEsperaEntradaCopyWith<$Res> {
  _$ListaEsperaEntradaCopyWithImpl(this._self, this._then);

  final ListaEsperaEntrada _self;
  final $Res Function(ListaEsperaEntrada) _then;

/// Create a copy of ListaEsperaEntrada
/// with the given fields replaced by the non-null parameter values.
@pragma('vm:prefer-inline') @override $Res call({Object? id = null,Object? recursoId = null,Object? fecha = null,Object? horaInicio = null,Object? horaFin = null,Object? estado = null,Object? createdAt = null,}) {
  return _then(ListaEsperaEntrada(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,recursoId: null == recursoId ? _self.recursoId : recursoId // ignore: cast_nullable_to_non_nullable
as int,fecha: null == fecha ? _self.fecha : fecha // ignore: cast_nullable_to_non_nullable
as String,horaInicio: null == horaInicio ? _self.horaInicio : horaInicio // ignore: cast_nullable_to_non_nullable
as String,horaFin: null == horaFin ? _self.horaFin : horaFin // ignore: cast_nullable_to_non_nullable
as String,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,
  ));
}

}


/// Adds pattern-matching-related methods to [ListaEsperaEntrada].
extension ListaEsperaEntradaPatterns on ListaEsperaEntrada {
/// A variant of `map` that fallback to returning `orElse`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeMap<TResult extends Object?>(TResult Function( _ListaEsperaEntrada value)?  $default,{required TResult orElse(),}){
final _that = this;
switch (_that) {
case _ListaEsperaEntrada() when $default != null:
return $default(_that);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// Callbacks receives the raw object, upcasted.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case final Subclass2 value:
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult map<TResult extends Object?>(TResult Function( _ListaEsperaEntrada value)  $default,){
final _that = this;
switch (_that) {
case _ListaEsperaEntrada():
return $default(_that);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `map` that fallback to returning `null`.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case final Subclass value:
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? mapOrNull<TResult extends Object?>(TResult? Function( _ListaEsperaEntrada value)?  $default,){
final _that = this;
switch (_that) {
case _ListaEsperaEntrada() when $default != null:
return $default(_that);case _:
  return null;

}
}
/// A variant of `when` that fallback to an `orElse` callback.
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return orElse();
/// }
/// ```

@optionalTypeArgs TResult maybeWhen<TResult extends Object?>(TResult Function( int id,  int recursoId,  String fecha,  String horaInicio,  String horaFin,  String estado,  String createdAt)?  $default,{required TResult orElse(),}) {final _that = this;
switch (_that) {
case _ListaEsperaEntrada() when $default != null:
return $default(_that.id,_that.recursoId,_that.fecha,_that.horaInicio,_that.horaFin,_that.estado,_that.createdAt);case _:
  return orElse();

}
}
/// A `switch`-like method, using callbacks.
///
/// As opposed to `map`, this offers destructuring.
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case Subclass2(:final field2):
///     return ...;
/// }
/// ```

@optionalTypeArgs TResult when<TResult extends Object?>(TResult Function( int id,  int recursoId,  String fecha,  String horaInicio,  String horaFin,  String estado,  String createdAt)  $default,) {final _that = this;
switch (_that) {
case _ListaEsperaEntrada():
return $default(_that.id,_that.recursoId,_that.fecha,_that.horaInicio,_that.horaFin,_that.estado,_that.createdAt);case _:
  throw StateError('Unexpected subclass');

}
}
/// A variant of `when` that fallback to returning `null`
///
/// It is equivalent to doing:
/// ```dart
/// switch (sealedClass) {
///   case Subclass(:final field):
///     return ...;
///   case _:
///     return null;
/// }
/// ```

@optionalTypeArgs TResult? whenOrNull<TResult extends Object?>(TResult? Function( int id,  int recursoId,  String fecha,  String horaInicio,  String horaFin,  String estado,  String createdAt)?  $default,) {final _that = this;
switch (_that) {
case _ListaEsperaEntrada() when $default != null:
return $default(_that.id,_that.recursoId,_that.fecha,_that.horaInicio,_that.horaFin,_that.estado,_that.createdAt);case _:
  return null;

}
}

}

/// @nodoc
@JsonSerializable()

class _ListaEsperaEntrada implements ListaEsperaEntrada {
  const _ListaEsperaEntrada({required this.id, required this.recursoId, required this.fecha, required this.horaInicio, required this.horaFin, required this.estado, required this.createdAt});
  factory _ListaEsperaEntrada.fromJson(Map<String, dynamic> json) => _$ListaEsperaEntradaFromJson(json);

@override final  int id;
@override final  int recursoId;
@override final  String fecha;
@override final  String horaInicio;
@override final  String horaFin;
@override final  String estado;
@override final  String createdAt;

/// Create a copy of ListaEsperaEntrada
/// with the given fields replaced by the non-null parameter values.
@override @JsonKey(includeFromJson: false, includeToJson: false)
@pragma('vm:prefer-inline')
_$ListaEsperaEntradaCopyWith<_ListaEsperaEntrada> get copyWith => __$ListaEsperaEntradaCopyWithImpl<_ListaEsperaEntrada>(this, _$identity);

@override
Map<String, dynamic> toJson() {
  return _$ListaEsperaEntradaToJson(this, );
}

@override
bool operator ==(Object other) {
  return identical(this, other) || (other.runtimeType == runtimeType&&other is _ListaEsperaEntrada&&(identical(other.id, id) || other.id == id)&&(identical(other.recursoId, recursoId) || other.recursoId == recursoId)&&(identical(other.fecha, fecha) || other.fecha == fecha)&&(identical(other.horaInicio, horaInicio) || other.horaInicio == horaInicio)&&(identical(other.horaFin, horaFin) || other.horaFin == horaFin)&&(identical(other.estado, estado) || other.estado == estado)&&(identical(other.createdAt, createdAt) || other.createdAt == createdAt));
}

@JsonKey(includeFromJson: false, includeToJson: false)
@override
int get hashCode => Object.hash(runtimeType,id,recursoId,fecha,horaInicio,horaFin,estado,createdAt);

@override
String toString() {
  return 'ListaEsperaEntrada(id: $id, recursoId: $recursoId, fecha: $fecha, horaInicio: $horaInicio, horaFin: $horaFin, estado: $estado, createdAt: $createdAt)';
}


}

/// @nodoc
abstract mixin class _$ListaEsperaEntradaCopyWith<$Res> implements $ListaEsperaEntradaCopyWith<$Res> {
  factory _$ListaEsperaEntradaCopyWith(_ListaEsperaEntrada value, $Res Function(_ListaEsperaEntrada) _then) = __$ListaEsperaEntradaCopyWithImpl;
@override @useResult
$Res call({
 int id, int recursoId, String fecha, String horaInicio, String horaFin, String estado, String createdAt
});




}
/// @nodoc
class __$ListaEsperaEntradaCopyWithImpl<$Res>
    implements _$ListaEsperaEntradaCopyWith<$Res> {
  __$ListaEsperaEntradaCopyWithImpl(this._self, this._then);

  final _ListaEsperaEntrada _self;
  final $Res Function(_ListaEsperaEntrada) _then;

/// Create a copy of ListaEsperaEntrada
/// with the given fields replaced by the non-null parameter values.
@override @pragma('vm:prefer-inline') $Res call({Object? id = null,Object? recursoId = null,Object? fecha = null,Object? horaInicio = null,Object? horaFin = null,Object? estado = null,Object? createdAt = null,}) {
  return _then(_ListaEsperaEntrada(
id: null == id ? _self.id : id // ignore: cast_nullable_to_non_nullable
as int,recursoId: null == recursoId ? _self.recursoId : recursoId // ignore: cast_nullable_to_non_nullable
as int,fecha: null == fecha ? _self.fecha : fecha // ignore: cast_nullable_to_non_nullable
as String,horaInicio: null == horaInicio ? _self.horaInicio : horaInicio // ignore: cast_nullable_to_non_nullable
as String,horaFin: null == horaFin ? _self.horaFin : horaFin // ignore: cast_nullable_to_non_nullable
as String,estado: null == estado ? _self.estado : estado // ignore: cast_nullable_to_non_nullable
as String,createdAt: null == createdAt ? _self.createdAt : createdAt // ignore: cast_nullable_to_non_nullable
as String,
  ));
}


}

// dart format on
